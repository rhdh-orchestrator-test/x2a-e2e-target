# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef infrastructure setup scripts and Ansible playbooks with InSpec tests. The primary focus appears to be demonstration examples rather than production infrastructure code. The migration scope is relatively small, with only a few Ansible playbooks and Chef server setup scripts to consider. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef server setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test file for verifying HTTPS website functionality and security
- `chef-and-ansible/index.html`: Possibly a static HTML file (content not examined)

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen**: Replace with Molecule for Ansible role testing
- **InSpec**: Can be retained as a testing framework, as it works well with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 and disables older protocols. This security hardening should be maintained in the migrated solution.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider implementing proper certificate management in production.
- **Hardcoded Credentials**: The Chef server setup scripts contain hardcoded credentials that should be replaced with Ansible Vault or another secure secret management solution:
  - Username: jtonello
  - Password: password (explicitly hardcoded)
  - Email: jtonello@chef.lab
  - Organization: lab

### Technical Challenges

- **Chef Server Replacement**: Determining the appropriate Ansible-based replacement for Chef Server functionality (AWX/Tower or alternative)
- **InSpec Integration**: Ensuring continued integration of InSpec tests with the new Ansible workflow
- **Certificate Management**: Implementing proper certificate management instead of self-signed certificates

### Migration Order

1. **website-https.yml** (already Ansible, low risk)
2. **poodle-fix.yml** (already Ansible, low risk)
3. **Chef Server Deployment Scripts** (high complexity, requires architectural decisions)

### Assumptions

1. The repository appears to be for demonstration purposes rather than production infrastructure
2. The Chef server setup scripts are used for setting up a Chef infrastructure that may manage other systems not represented in this repository
3. The Ansible playbooks are examples showing how to use InSpec with Ansible rather than production infrastructure code
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. The migration goal is to standardize on Ansible and eliminate Chef dependencies
6. InSpec will continue to be used for compliance testing with Ansible

## Migration Recommendations

1. **Retain Existing Ansible Playbooks**: The website_https.yml and poodle_fix.yml playbooks are already in Ansible format and only need minor updates for best practices.

2. **Replace Chef Server Setup**: Create Ansible playbooks to replace the Chef server setup scripts, focusing on the configuration management aspects rather than deploying Chef itself.

3. **Enhance Testing Framework**: Maintain the InSpec tests but integrate them with Molecule for more comprehensive Ansible role testing.

4. **Implement Secret Management**: Replace hardcoded credentials with Ansible Vault or another secure secret management solution.

5. **Documentation**: Create documentation explaining the migration from Chef to Ansible, especially for teams familiar with the Chef ecosystem.