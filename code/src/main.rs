use chrono::Local;
use std::env;
use std::path::Path;

#[cfg(target_os = "windows")]
mod windows_impl;

#[cfg(target_os = "macos")]
mod macos_impl;

#[derive(Debug)]
struct WindowInfo {
    id: String,
    pid: u32,
    title: String,
}

enum Selection {
    Title(String),
    Pid(u32),
    Id(String),
}

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() == 1 {
        print_help();
        return;
    }

    let (selection, output_path) = parse_args(&args[1..]);

    let selection = match selection {
        Some(s) => s,
        None => {
            eprintln!("Error: Invalid arguments");
            std::process::exit(1);
        }
    };

    let windows = enumerate_windows();

    let window = match &selection {
        Selection::Title(title) => windows.iter().find(|w| w.title == *title),
        Selection::Pid(pid) => windows.iter().find(|w| w.pid == *pid),
        Selection::Id(id) => windows.iter().find(|w| w.id == *id),
    };

    let window = match window {
        Some(w) => w,
        None => {
            eprintln!("Error: No matching window found");
            std::process::exit(1);
        }
    };

    let final_path = resolve_output_path(output_path);

    capture_window(&window.id, &final_path);

    println!("Wrote {}", final_path);
}

// $REQ_HELP_001
fn print_help() {
    println!("Usage: screenshot.exe [OPTIONS] [OUTPUT]");
    println!();
    println!("Options:");
    println!("  --title \"window title\" [output.png|directory|]");
    println!("  --pid <process-id> [output.png|directory|]");
    println!("  --id <window-id> [output.png|directory|]");
    println!();
    println!("Output:");
    println!("  - Specify .png file: saves to that exact location");
    println!("  - Specify directory: saves with timestamped filename");
    println!("  - Omit output: saves to current directory with timestamped filename");
    println!();
    println!("Currently open windows (id,pid,title):");

    let windows = enumerate_windows();
    for w in windows {
        println!("{}\t{}\t\"{}\"", w.id, w.pid, w.title);
    }
}

fn parse_args(args: &[String]) -> (Option<Selection>, Option<String>) {
    let mut selection: Option<Selection> = None;
    let mut output: Option<String> = None;
    let mut i = 0;

    while i < args.len() {
        let arg = &args[i];

        if arg == "--title" && i + 1 < args.len() {
            selection = Some(Selection::Title(args[i + 1].clone()));
            i += 2;
        } else if arg == "--pid" && i + 1 < args.len() {
            if let Ok(pid) = args[i + 1].parse::<u32>() {
                selection = Some(Selection::Pid(pid));
            }
            i += 2;
        } else if arg == "--id" && i + 1 < args.len() {
            selection = Some(Selection::Id(args[i + 1].clone()));
            i += 2;
        } else if !arg.starts_with("--") {
            if selection.is_none() {
                // Auto-detect: if starts with quote, it's a title
                if arg.starts_with('"') {
                    let title = arg.trim_matches('"').to_string();
                    selection = Some(Selection::Title(title));
                } else if let Ok(pid) = arg.parse::<u32>() {
                    // Try as PID first, but could also be window ID
                    // Check if it matches a window ID first
                    let windows = enumerate_windows();
                    if windows.iter().any(|w| w.id == *arg) {
                        selection = Some(Selection::Id(arg.clone()));
                    } else {
                        selection = Some(Selection::Pid(pid));
                    }
                } else {
                    // Assume window ID
                    selection = Some(Selection::Id(arg.clone()));
                }
            } else {
                output = Some(arg.clone());
            }
            i += 1;
        } else {
            i += 1;
        }
    }

    (selection, output)
}

fn resolve_output_path(output: Option<String>) -> String {
    let timestamp = Local::now().format("%Y-%m-%d-%H-%M-%S-%6f").to_string();
    let default_filename = format!("{}_screenshot.png", timestamp);

    match output {
        Some(path) => {
            if path.ends_with(".png") {
                path
            } else if Path::new(&path).is_dir() || path.ends_with('/') || path.ends_with('\\') {
                let path = path.trim_end_matches(['/', '\\']);
                format!("{}/{}", path, default_filename)
            } else {
                // Treat as directory
                format!("{}/{}", path, default_filename)
            }
        }
        None => format!("./{}", default_filename),
    }
}

#[cfg(target_os = "windows")]
fn enumerate_windows() -> Vec<WindowInfo> {
    windows_impl::enumerate_windows()
}

#[cfg(target_os = "macos")]
fn enumerate_windows() -> Vec<WindowInfo> {
    macos_impl::enumerate_windows()
}

#[cfg(target_os = "windows")]
fn capture_window(window_id: &str, output_path: &str) {
    windows_impl::capture_window(window_id, output_path)
}

#[cfg(target_os = "macos")]
fn capture_window(window_id: &str, output_path: &str) {
    macos_impl::capture_window(window_id, output_path)
}
