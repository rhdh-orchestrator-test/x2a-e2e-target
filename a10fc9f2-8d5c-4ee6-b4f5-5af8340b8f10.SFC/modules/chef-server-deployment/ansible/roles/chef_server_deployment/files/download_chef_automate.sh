#!/bin/bash
# Download Chef Automate CLI
curl https://packages.chef.io/files/current/latest/chef-automate-cli/chef-automate_linux_amd64.zip | gunzip - > /tmp/chef-automate
chmod +x /tmp/chef-automate