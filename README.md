# Chameleon GUI
A local graphical interface for Chameleon Cloud built on the OpenStack CLI.

## Overview
Chameleon GUI provides a simple and intuitive graphical interface for managing virtual (KVM) and baremetal (CHI) instances on Chameleon Cloud, removing the need to manually use OpenStack commands.  
It uses Tkinter for the GUI and Python modules interacting with the OpenStack CLI to handle cloud resources efficiently.

## Features
- Manage both **KVM** and **CHI (baremetal)** environments  
- Launch and delete instances through a clean GUI  
- Automatically associate and release floating IPs  
- View and select available images, flavors, networks, and security groups  
- Persist authentication through Application Credentials  
- Simplified interface based on `python-openstackclient` and `python-blazarclient`
