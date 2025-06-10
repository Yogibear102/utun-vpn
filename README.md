VPN Client (macOS utun)
A simple Python VPN client for macOS that uses a utun virtual network interface and forwards traffic to a VPN server over TCP.

Features
Connects to a VPN server via TCP
Uses macOS utun device for virtual networking
Forwards packets between your system and the VPN server
Requirements
Python 3.12+
macOS (utun support)
Root privileges (to access utun devices)
Usage
Clone this repository.
Create and activate a Python virtual environment (see pyvenv.cfg for details).
Run the client:
Files
client.py — The VPN client source code.
pyvenv.cfg — Python virtual environment configuration.
