use std::collections::VecDeque;
use std::fs::{self, File, OpenOptions};
use std::io::{self, BufReader, BufWriter, Read, Seek, SeekFrom, Write};
use std::path::{Path, PathBuf};

// Each subpart holds 0xcc blocks of 0x1000 bytes = 0xcc000 bytes of data
const SUBPART_DATA_SIZE: usize = 0xcc000;
// Hash list between each subpart in a GOD part file
const HASH_LIST_SIZE: u64 = 0x1000;
// Each GOD part file starts with 0x1000 master hash + 0x1000 first sub-hash = 0x2000 to skip
const PART_HEADER_SKIP: u64 = 0x2000;

// XSF marker at offset 0x2000 in Data0000 means the ISO header is already embedded
const XSF_MARKER: [u8; 3] = [0x58, 0x53, 0x46]; // "XSF"

// The XSF/ISO header template (65536 bytes), embedded at compile time
const XSF_HEADER: &[u8] = include_bytes!("../XSFHeader.bin");

const APP_NAME: &[u8] = b"God2Iso v1.0";

fn usage() {
    eprintln!("Usage: god2iso <god_package_file> <output_dir> [--fix]");
    eprintln!();
    eprintln!("  god_package_file  Path to the GOD package header file (not the .data folder).");
    eprintln!("                    The associated <name>.data/ directory must exist alongside it.");
    eprintln!("  output_dir        Directory to write the resulting .iso file into.");
    eprintln!("  --fix             Also apply the CreateIsoGood header fix.");
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().collect();

    if args.len() < 3 {
        usage();
        std::process::exit(1);
    }

    let god_path = PathBuf::from(&args[1]);
    let output_dir = PathBuf::from(&args[2]);
    let fix = args.iter().any(|a| a == "--fix");

    if !god_path.exists() {
        eprintln!("Error: GOD package file not found: {}", god_path.display());
        std::process::exit(1);
    }
    if !output_dir.is_dir() {
        eprintln!("Error: output directory does not exist: {}", output_dir.display());
        std::process::exit(1);
    }

    let base_name = god_path
        .file_name()
        .ok_or("invalid god_package_file path")?
        .to_string_lossy()
        .into_owned();

    let data_dir = PathBuf::from(format!("{}.data", god_path.display()));
    if !data_dir.is_dir() {
        eprintln!(
            "Error: associated data directory not found: {}",
            data_dir.display()
        );
        std::process::exit(1);
    }

    // Count how many Data#### files exist
    let mut part_count: usize = 0;
    loop {
        let part_path = data_dir.join(format!("Data{:04}", part_count));
        if !part_path.exists() {
            break;
        }
        part_count += 1;
    }

    if part_count == 0 {
        eprintln!("Error: no Data#### files found in {}", data_dir.display());
        std::process::exit(1);
    }

    eprintln!("Found {} data part(s).", part_count);

    // Check whether Data0000 already has an embedded XSF marker
    let first_data = data_dir.join("Data0000");
    let has_xsf = check_xsf_marker(&first_data)?;

    let iso_path = output_dir.join(format!("{}.iso", base_name));
    eprintln!("Output: {}", iso_path.display());

    // Write the ISO
    {
        let iso_file = File::create(&iso_path)?;
        let mut iso = BufWriter::new(iso_file);

        if !has_xsf {
            iso.write_all(XSF_HEADER)?;
        }

        for i in 0..part_count {
            let part_path = data_dir.join(format!("Data{:04}", i));
            eprintln!("  Processing part {}/{}: {}", i + 1, part_count, part_path.display());

            let part_file = File::open(&part_path)?;
            let mut reader = BufReader::new(part_file);
            // Skip master hash list + first sub-hash list
            reader.seek(SeekFrom::Start(PART_HEADER_SKIP))?;

            let mut data_buf = vec![0u8; SUBPART_DATA_SIZE];
            let mut hash_buf = vec![0u8; HASH_LIST_SIZE as usize];

            loop {
                // Read a data block
                let n = read_up_to(&mut reader, &mut data_buf)?;
                if n == 0 {
                    break;
                }
                iso.write_all(&data_buf[..n])?;
                if n < SUBPART_DATA_SIZE {
                    break;
                }
                // Skip the following hash block
                let hn = read_up_to(&mut reader, &mut hash_buf)?;
                if hn < HASH_LIST_SIZE as usize {
                    break;
                }
            }
        }

        iso.flush()?;
    }

    // Fix headers if needed (requires read+write)
    if !has_xsf {
        let mut iso_rw = OpenOptions::new().read(true).write(true).open(&iso_path)?;
        fix_xfs_header(&mut iso_rw)?;
        fix_sector_offsets(&mut iso_rw, &god_path)?;
    }

    if fix {
        let mut iso_rw = OpenOptions::new().read(true).write(true).open(&iso_path)?;
        fix_create_iso_good_header(&mut iso_rw)?;
    }

    eprintln!("Done.");
    Ok(())
}

/// Read as many bytes as possible into buf; returns the number of bytes read.
fn read_up_to<R: Read>(reader: &mut R, buf: &mut [u8]) -> io::Result<usize> {
    let mut total = 0;
    while total < buf.len() {
        match reader.read(&mut buf[total..]) {
            Ok(0) => break,
            Ok(n) => total += n,
            Err(e) if e.kind() == io::ErrorKind::Interrupted => {}
            Err(e) => return Err(e),
        }
    }
    Ok(total)
}

/// Check if Data0000 has the XSF marker at offset 0x2000.
fn check_xsf_marker(data0000: &Path) -> io::Result<bool> {
    let mut f = File::open(data0000)?;
    f.seek(SeekFrom::Start(0x2000))?;
    let mut buf = [0u8; 3];
    f.read_exact(&mut buf)?;
    Ok(buf == XSF_MARKER)
}

/// Fix the XSF/ISO header size fields and tool name stamp.
fn fix_xfs_header<F: Read + Write + Seek>(iso: &mut F) -> io::Result<()> {
    let len = iso.seek(SeekFrom::End(0))?;

    // Offset 8: data size (iso.Length - 0x400) as LE i64
    iso.seek(SeekFrom::Start(8))?;
    iso.write_all(&((len - 0x400) as i64).to_le_bytes())?;

    // Offset 0x8050: volume size in sectors as LE u32 then BE u32
    let vol_size = (len / 2048) as u32;
    iso.seek(SeekFrom::Start(0x8050))?;
    iso.write_all(&vol_size.to_le_bytes())?;
    iso.write_all(&vol_size.to_be_bytes())?;

    // Offset 0x7a69: tool name stamp
    iso.seek(SeekFrom::Start(0x7a69))?;
    iso.write_all(APP_NAME)?;

    Ok(())
}

/// Fix sector offsets in the ISO directory table based on the GOD package header.
fn fix_sector_offsets<F: Read + Write + Seek>(iso: &mut F, god_path: &Path) -> io::Result<()> {
    let god_bytes = fs::read(god_path)?;

    // Check if the offset-type flag is set at byte 0x391
    if (god_bytes.get(0x391).copied().unwrap_or(0) & 0x40) != 0x40 {
        return Ok(());
    }

    // Read the raw offset correction value at bytes 0x395..0x399 (LE i32)
    if god_bytes.len() < 0x399 {
        return Ok(());
    }
    let raw_offset = i32::from_le_bytes([
        god_bytes[0x395],
        god_bytes[0x396],
        god_bytes[0x397],
        god_bytes[0x398],
    ]);
    if raw_offset == 0 {
        return Ok(());
    }
    let offset = raw_offset * 2 - 34;

    // Read the root directory sector from the ISO at 0x10014
    let mut buf4 = [0u8; 4];
    iso.seek(SeekFrom::Start(0x10014))?;
    iso.read_exact(&mut buf4)?;
    let root_sector = i32::from_le_bytes(buf4);

    if root_sector <= 0 {
        return Ok(());
    }

    // Fix root sector and queue the root directory for traversal
    let corrected_root = root_sector - offset;
    iso.seek(SeekFrom::Start(0x10014))?;
    iso.write_all(&corrected_root.to_le_bytes())?;

    iso.read_exact(&mut buf4)?;
    let root_size = i32::from_le_bytes(buf4);

    let mut dirs: VecDeque<(i32, i32)> = VecDeque::new();
    dirs.push_back((corrected_root, root_size));

    // Traverse the XISO directory tree and correct all sector references
    while let Some((sector, size)) = dirs.pop_front() {
        let start_pos = sector as u64 * 2048;
        let end_pos = start_pos + size as u64;

        iso.seek(SeekFrom::Start(start_pos))?;

        loop {
            let cur = iso.seek(SeekFrom::Current(0))?;
            if cur + 4 >= end_pos {
                break;
            }

            // Detect sector boundary crossing
            if (cur + 4) / 2048 > cur / 2048 {
                let next = (cur / 2048 + 1) * 2048;
                iso.seek(SeekFrom::Start(next))?;
                continue;
            }

            // Read left/right subtree offsets (used as a sentinel check)
            iso.read_exact(&mut buf4)?;
            if buf4 == [0xff, 0xff, 0xff, 0xff] {
                // Sentinel: possibly another sector to process
                let cur2 = iso.seek(SeekFrom::Current(0))?;
                if end_pos - cur2 > 2048 {
                    let next = (cur2 / 2048 + 1) * 2048;
                    iso.seek(SeekFrom::Start(next))?;
                    continue;
                }
                break;
            }

            // Read and correct the entry's sector number
            iso.read_exact(&mut buf4)?;
            let entry_sector = i32::from_le_bytes(buf4);
            if entry_sector > 0 {
                let corrected = entry_sector - offset;
                iso.seek(SeekFrom::Current(-4))?;
                iso.write_all(&corrected.to_le_bytes())?;
            } else {
                iso.seek(SeekFrom::Current(0))?;
            }

            // Read size
            iso.read_exact(&mut buf4)?;
            let entry_size = i32::from_le_bytes(buf4);

            // Read attributes byte
            let mut attr = [0u8; 1];
            iso.read_exact(&mut attr)?;

            // If directory, enqueue for traversal
            if (attr[0] & 0x10) == 0x10 {
                dirs.push_back((entry_sector - offset, entry_size));
            }

            // Read filename length and skip filename + padding
            iso.read_exact(&mut attr)?;
            let name_len = attr[0] as u64;
            iso.seek(SeekFrom::Current(name_len as i64))?;
            let record_len = 14 + name_len;
            if record_len % 4 != 0 {
                iso.seek(SeekFrom::Current((4 - record_len % 4) as i64))?;
            }
        }
    }

    Ok(())
}

/// Apply the CreateIsoGood header fix if the ISO was created by that tool.
fn fix_create_iso_good_header<F: Read + Write + Seek>(iso: &mut F) -> io::Result<()> {
    iso.seek(SeekFrom::Start(8))?;
    let mut buf = [0u8; 8];
    iso.read_exact(&mut buf)?;
    let val = i64::from_le_bytes(buf);
    // 2587648 = 0x277C00 — CreateIsoGood signature value
    if val == 2_587_648 {
        iso.seek(SeekFrom::Start(0))?;
        iso.write_all(XSF_HEADER)?;
        fix_xfs_header(iso)?;
    }
    Ok(())
}
