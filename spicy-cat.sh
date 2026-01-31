#!/bin/bash
#
#     /\_____/\
#    /  o   o  \
#   ( ==  ^  == )
#    )         (
#   (           )
#  ( (  )   (  ) )
# (__(__)___(__)__)
#
# spicy-cat - Digital anonymity tool
# Bash wrapper for installation and system integration
#
# "A cat has absolute emotional honesty. The internet has none.
#  This tool helps balance the scales."
#

set -e

# Colors (because even scripts deserve to look good)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${HOME}/.local/share/spicy-cat"
BIN_DIR="${HOME}/.local/bin"
CONFIG_DIR="${HOME}/.spicy-cat"

# Cat ASCII art (compact version)
print_cat() {
    echo -e "${MAGENTA}"
    echo " /\\_/\\"
    echo "( o.o )"
    echo " > ^ <"
    echo -e "${NC}"
}

# Print styled message
msg() {
    echo -e "${CYAN}[spicy-cat]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[spicy-cat]${NC} $1"
}

error() {
    echo -e "${RED}[spicy-cat]${NC} $1"
}

success() {
    echo -e "${GREEN}[spicy-cat]${NC} $1"
}

# Check Python version
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
            success "Python $PYTHON_VERSION found"
            return 0
        else
            error "Python 3.8+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        error "Python 3 not found"
        return 1
    fi
}

# Check for optional dependencies
check_dependencies() {
    msg "Checking dependencies..."

    # Required: Python 3.8+
    check_python || exit 1

    # Optional: Faker
    if python3 -c "import faker" 2>/dev/null; then
        success "Faker: installed (rich identity data)"
    else
        warn "Faker: not installed (using builtin data)"
        echo -e "   ${BOLD}Install with:${NC} pip install faker"
    fi

    # Optional: cryptography
    if python3 -c "import cryptography" 2>/dev/null; then
        success "cryptography: installed (secure storage)"
    else
        warn "cryptography: not installed (using basic obfuscation)"
        echo -e "   ${BOLD}Install with:${NC} pip install cryptography"
    fi

    # Optional: Firefox
    if command -v firefox &> /dev/null; then
        success "Firefox: installed"
    else
        warn "Firefox: not found (browse command won't work)"
    fi

    # Optional: Tor
    if systemctl is-active --quiet tor 2>/dev/null || pgrep -x tor > /dev/null; then
        success "Tor: running"
    elif command -v tor &> /dev/null; then
        warn "Tor: installed but not running"
        echo -e "   ${BOLD}Start with:${NC} sudo systemctl start tor"
    else
        warn "Tor: not installed (--tor flag won't work)"
        echo -e "   ${BOLD}Install with:${NC} sudo apt install tor"
    fi

    echo ""
}

# Install spicy-cat
install() {
    print_cat
    echo -e "${BOLD}${CYAN}Installing spicy-cat${NC}"
    echo ""

    check_dependencies

    msg "Creating directories..."
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    mkdir -p "$CONFIG_DIR"

    msg "Copying files..."
    cp -r "$SCRIPT_DIR"/*.py "$INSTALL_DIR/" 2>/dev/null || true
    cp -r "$SCRIPT_DIR"/lib "$INSTALL_DIR/"
    cp -r "$SCRIPT_DIR"/data "$INSTALL_DIR/" 2>/dev/null || true

    msg "Creating launcher..."
    cat > "$BIN_DIR/spicy-cat" << 'LAUNCHER'
#!/bin/bash
INSTALL_DIR="${HOME}/.local/share/spicy-cat"
exec python3 "$INSTALL_DIR/spicy-cat.py" "$@"
LAUNCHER
    chmod +x "$BIN_DIR/spicy-cat"

    # Add to PATH if needed
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        warn "$BIN_DIR is not in PATH"
        echo ""
        echo "Add this to your ~/.bashrc or ~/.zshrc:"
        echo -e "${BOLD}  export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
        echo ""
    fi

    success "Installation complete!"
    echo ""
    echo -e "${BOLD}Quick start:${NC}"
    echo "  spicy-cat new          # Generate identity"
    echo "  spicy-cat dashboard    # View status"
    echo "  spicy-cat browse       # Launch browser"
    echo ""
    echo -e "${MAGENTA}Stay anonymous, stay curious. =^.^=${NC}"
}

# Uninstall spicy-cat
uninstall() {
    print_cat
    echo -e "${BOLD}${YELLOW}Uninstalling spicy-cat${NC}"
    echo ""

    # Confirm
    read -p "This will remove spicy-cat and all identities. Continue? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        msg "Cancelled."
        exit 0
    fi

    msg "Stopping daemon if running..."
    "$BIN_DIR/spicy-cat" daemon stop 2>/dev/null || true

    msg "Removing files..."
    rm -rf "$INSTALL_DIR"
    rm -f "$BIN_DIR/spicy-cat"

    read -p "Remove saved identities too? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$CONFIG_DIR"
        success "Identities removed"
    fi

    success "Uninstalled. Goodbye!"
    echo -e "${MAGENTA}The cat has left the building. =^.^=${NC}"
}

# Install recommended dependencies
install_deps() {
    print_cat
    echo -e "${BOLD}${CYAN}Installing recommended dependencies${NC}"
    echo ""

    # Detect package manager
    if command -v apt &> /dev/null; then
        msg "Detected Debian/Ubuntu"

        echo -e "${BOLD}System packages:${NC}"
        sudo apt update
        sudo apt install -y python3 python3-pip firefox tor

    elif command -v dnf &> /dev/null; then
        msg "Detected Fedora/RHEL"
        sudo dnf install -y python3 python3-pip firefox tor

    elif command -v pacman &> /dev/null; then
        msg "Detected Arch Linux"
        sudo pacman -Sy --noconfirm python python-pip firefox tor

    else
        warn "Unknown package manager. Install manually:"
        echo "  - python3"
        echo "  - firefox"
        echo "  - tor"
    fi

    echo ""
    echo -e "${BOLD}Python packages:${NC}"
    pip3 install --user faker cryptography

    success "Dependencies installed!"
}

# Run directly without installing
run() {
    exec python3 "$SCRIPT_DIR/spicy-cat.py" "${@:2}"
}

# Quick identity generation (no install needed)
quick() {
    python3 "$SCRIPT_DIR/spicy-cat.py" new --temp
}

# Show help
show_help() {
    print_cat
    echo -e "${BOLD}spicy-cat.sh${NC} - Installation and management script"
    echo ""
    echo -e "${BOLD}Usage:${NC}"
    echo "  ./spicy-cat.sh install      Install spicy-cat"
    echo "  ./spicy-cat.sh uninstall    Remove spicy-cat"
    echo "  ./spicy-cat.sh deps         Install dependencies"
    echo "  ./spicy-cat.sh run [args]   Run without installing"
    echo "  ./spicy-cat.sh quick        Quick throwaway identity"
    echo "  ./spicy-cat.sh check        Check dependencies"
    echo "  ./spicy-cat.sh help         Show this help"
    echo ""
    echo -e "${BOLD}After installation:${NC}"
    echo "  spicy-cat new          Generate identity"
    echo "  spicy-cat list         List identities"
    echo "  spicy-cat browse       Launch anonymous browser"
    echo "  spicy-cat dashboard    Live status view"
    echo ""
    echo -e "${MAGENTA}\"On the internet, nobody knows you're a cat.\"${NC}"
}

# Main
case "${1:-}" in
    install)
        install
        ;;
    uninstall)
        uninstall
        ;;
    deps|dependencies)
        install_deps
        ;;
    run)
        run "$@"
        ;;
    quick)
        quick
        ;;
    check)
        print_cat
        check_dependencies
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        error "Unknown command: $1"
        echo "Use './spicy-cat.sh help' for usage"
        exit 1
        ;;
esac
