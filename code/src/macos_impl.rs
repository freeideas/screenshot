use crate::WindowInfo;
use core_foundation::base::{CFType, TCFType};
use core_foundation::boolean::CFBoolean;
use core_foundation::dictionary::CFDictionary;
use core_foundation::number::CFNumber;
use core_foundation::string::CFString;
use core_graphics::display::{
    kCGNullWindowID, kCGWindowImageDefault, kCGWindowListOptionIncludingWindow, CGWindowID,
    CGWindowListCopyWindowInfo,
};
use core_graphics::window::{kCGWindowListOptionAll, kCGWindowListOptionOnScreenOnly};
use image::{ImageBuffer, Rgba};
use std::path::Path;

pub fn enumerate_windows() -> Vec<WindowInfo> {
    let mut windows: Vec<WindowInfo> = Vec::new();

    unsafe {
        let window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly | kCGWindowListOptionAll,
            kCGNullWindowID,
        );

        if window_list.is_null() {
            return windows;
        }

        // Use wrap_under_create_rule since CGWindowListCopyWindowInfo returns a retained object
        let array = core_foundation::array::CFArray::<CFDictionary<CFString, CFType>>::wrap_under_create_rule(window_list as _);
        let count = array.len();

        for i in 0..count {
            let dict = array.get(i as isize);
            if let Some(dict) = dict {
                let window_id = get_window_number(&dict);
                let pid = get_window_pid(&dict);
                let title = get_window_name(&dict);
                let on_screen = get_window_on_screen(&dict);

                if on_screen && !title.is_empty() {
                    windows.push(WindowInfo {
                        id: format!("{:X}", window_id),
                        pid,
                        title,
                    });
                }
            }
        }
    }

    windows
}

fn get_window_number(dict: &CFDictionary<CFString, CFType>) -> u32 {
    let key = CFString::new("kCGWindowNumber");
    if let Some(value) = dict.find(&key) {
        if let Some(num) = value.downcast::<CFNumber>() {
            return num.to_i32().unwrap_or(0) as u32;
        }
    }
    0
}

fn get_window_pid(dict: &CFDictionary<CFString, CFType>) -> u32 {
    let key = CFString::new("kCGWindowOwnerPID");
    if let Some(value) = dict.find(&key) {
        if let Some(num) = value.downcast::<CFNumber>() {
            return num.to_i32().unwrap_or(0) as u32;
        }
    }
    0
}

fn get_window_name(dict: &CFDictionary<CFString, CFType>) -> String {
    let key = CFString::new("kCGWindowName");
    if let Some(value) = dict.find(&key) {
        if let Some(s) = value.downcast::<CFString>() {
            return s.to_string();
        }
    }
    // Fall back to owner name
    let key = CFString::new("kCGWindowOwnerName");
    if let Some(value) = dict.find(&key) {
        if let Some(s) = value.downcast::<CFString>() {
            return s.to_string();
        }
    }
    String::new()
}

fn get_window_on_screen(dict: &CFDictionary<CFString, CFType>) -> bool {
    let key = CFString::new("kCGWindowIsOnscreen");
    if let Some(value) = dict.find(&key) {
        if let Some(b) = value.downcast::<CFBoolean>() {
            return b == CFBoolean::true_value();
        }
    }
    true
}

pub fn capture_window(window_id: &str, output_path: &str) {
    let window_num = u32::from_str_radix(window_id, 16).unwrap_or(0);

    unsafe {
        let cg_image = core_graphics::display::CGDisplay::screenshot(
            core_graphics::display::CGRectNull,
            kCGWindowListOptionIncludingWindow,
            window_num as CGWindowID,
            kCGWindowImageDefault,
        );

        let cg_image = match cg_image {
            Some(img) => img,
            None => {
                eprintln!("Error: Failed to capture window");
                std::process::exit(1);
            }
        };

        let width = cg_image.width();
        let height = cg_image.height();
        let bytes_per_row = cg_image.bytes_per_row();
        let data = cg_image.data();

        let mut pixels: Vec<u8> = Vec::with_capacity(width * height * 4);

        for y in 0..height {
            for x in 0..width {
                let offset = y * bytes_per_row + x * 4;
                // Core Graphics uses BGRA on macOS
                let b = data.bytes()[offset];
                let g = data.bytes()[offset + 1];
                let r = data.bytes()[offset + 2];
                let a = data.bytes()[offset + 3];
                pixels.push(r);
                pixels.push(g);
                pixels.push(b);
                pixels.push(a);
            }
        }

        let img: ImageBuffer<Rgba<u8>, Vec<u8>> =
            ImageBuffer::from_raw(width as u32, height as u32, pixels).unwrap();

        if let Some(parent) = Path::new(output_path).parent() {
            if !parent.as_os_str().is_empty() {
                let _ = std::fs::create_dir_all(parent);
            }
        }

        img.save(output_path).unwrap();
    }
}
