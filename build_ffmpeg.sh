#!/bin/bash
set -e

echo "Starting FFmpeg compilation process on Debian 12 (Bookworm)..."

# Update and install necessary dependencies
echo "Installing required packages..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
    build-essential \
    yasm \
    nasm \
    cmake \
    git \
    pkg-config \
    libtool \
    libssl-dev \
    zlib1g-dev \
    libx264-dev \
    libvpx-dev \
    libmp3lame-dev \
    libopus-dev \
    libvorbis-dev \
    libdav1d-dev \
    libass-dev \
    libfreetype6-dev \
    libfontconfig1-dev \
    libtheora-dev \
    libsdl2-dev \
    libxcb1-dev \
    libxcb-shm0-dev \
    libxcb-xfixes0-dev \
    texinfo \
    wget \
    gnutls-bin \
    libgnutls28-dev \
    autoconf \
    automake \
    mercurial

# Set up directories
echo "Setting up directories..."
FFMPEG_BUILD_DIR="$HOME/ffmpeg_build"
FFMPEG_SRC_DIR="$HOME/ffmpeg_sources"
mkdir -p "$FFMPEG_BUILD_DIR" "$FFMPEG_SRC_DIR"

# Build libfdk-aac
echo "Downloading and building libfdk-aac..."
if [ ! -d "$FFMPEG_SRC_DIR/fdk-aac" ]; then
    cd "$FFMPEG_SRC_DIR"
    git clone https://github.com/mstorsjo/fdk-aac.git
fi
cd "$FFMPEG_SRC_DIR/fdk-aac"
autoreconf -fiv
./configure --prefix="$FFMPEG_BUILD_DIR" --disable-shared
make -j$(nproc)
make install

# Build x265
echo "Downloading and building x265..."
if [ ! -d "$FFMPEG_SRC_DIR/x265_git" ]; then
    cd "$FFMPEG_SRC_DIR"
    git clone https://github.com/videolan/x265.git x265_git
fi
cd "$FFMPEG_SRC_DIR/x265_git/build/linux"
cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="$FFMPEG_BUILD_DIR" -DENABLE_SHARED=off ../../source
make -j$(nproc)
make install

# Download and build FFmpeg
echo "Downloading FFmpeg source code..."
if [ ! -d "$FFMPEG_SRC_DIR/FFmpeg" ]; then
    cd "$FFMPEG_SRC_DIR"
    git clone --depth=1 https://github.com/FFmpeg/FFmpeg.git
fi
cd "$FFMPEG_SRC_DIR/FFmpeg"

echo "Configuring and compiling FFmpeg..."
PATH="$FFMPEG_BUILD_DIR/bin:$PATH"
PKG_CONFIG_PATH="$FFMPEG_BUILD_DIR/lib/pkgconfig" ./configure \
    --prefix="$FFMPEG_BUILD_DIR" \
    --pkg-config-flags="--static" \
    --extra-cflags="-I$FFMPEG_BUILD_DIR/include" \
    --extra-ldflags="-L$FFMPEG_BUILD_DIR/lib" \
    --extra-libs="-lpthread -lm" \
    --bindir="$HOME/bin" \
    --enable-gpl \
    --enable-nonfree \
    --enable-libx264 \
    --enable-libx265 \
    --enable-libvpx \
    --enable-libfdk-aac \
    --enable-libmp3lame \
    --enable-libopus \
    --enable-libvorbis \
    --enable-libdav1d \
    --enable-libass \
    --enable-libfreetype \
    --enable-libtheora \
    --enable-libfontconfig \
    --enable-libxcb \
    --enable-openssl \
    --enable-sdl2

make -j$(nproc)
make install

# Add FFmpeg to PATH
echo "Adding FFmpeg to PATH..."
if ! grep -q "$HOME/bin" <<< "$PATH"; then
    echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/bin:$PATH"
fi

echo "FFmpeg compilation and installation complete! Use 'ffmpeg' command to verify."

