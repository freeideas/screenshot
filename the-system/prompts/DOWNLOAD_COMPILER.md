# Download Compiler

Ensure the required compiler is available for building the project.

**First:** Read `./README.md` to determine which compiler/language the project uses. If it isn't obvious, then try reading `./specs/*.md` documents. 

## Process

1. **Check PATH** -- Run the compiler's version command to check if it's already available on PATH
2. **Check ./compiler/** -- If not on PATH, check if it exists in `./compiler/` directory
3. **If available** -- Do nothing, the compiler is ready to use
4. **If not available** -- Download a portable/standalone version into `./compiler/` and verify it works

## Requirements

- Download portable/standalone builds (not installers)
- Extract to `./compiler/` directory
- Use the compiler from `./compiler/` in build scripts
- The `./compiler/` directory is gitignored

## Examples

These are the compilers you may need to download portably:

| Language | Test Command       | Portable Location                |
| -------- | ------------------ | -------------------------------- |
| Rust     | `rustc --version`  | `./compiler/cargo/bin/rustc.exe` |
| Zig      | `zig version`      | `./compiler/zig/zig.exe`         |
| C#       | `dotnet --version` | `./compiler/dotnet/dotnet.exe`   |
| Go       | `go version`       | `./compiler/go/bin/go.exe`       |
| Java     | `javac -version`   | `./compiler/jdk/bin/javac.exe`   |

