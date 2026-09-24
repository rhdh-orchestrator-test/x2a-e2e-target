# MIGRATION FROM MIXED CHEF/ANSIBLE TO ANSIBLE

This repository is a demonstration/example collection showing Chef InSpec integration with Ansible playbooks, rather than a traditional Chef cookbook repository requiring migration. The primary content is already in Ansible format with Chef InSpec used for compliance testing. Migration complexity is minimal as the core infrastructure automation is already Ansible-based.

## Module Migration Plan

This repository contains example Ansible playbooks and Chef InSpec tests that demonstrate compliance automation patterns:

### MODULE INVENTORY

**ansible-apache-https**:
- Description: Apache web server with HTTPS/SSL configuration, self-signed certificate generation, and virtual host setup for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible
- Key Features: SSL certificate generation via OpenSSL modules, Apache virtual host configuration, package management for Ubuntu 20.04

**ansible-ssl-hardening**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols (POODLE fix) and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible
- Key Features: Apache SSL configuration hardening, protocol restriction, service restart handling

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Static HTML test content for web server validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script for on-premises/cloud VMs
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script without Automate

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml and playbooks)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen for local development/testing)
- **Cloud Platform**: Not specified (deployment scripts support both on-premises and cloud VMs)

## Migration Approach

### Key Dependencies to Address

**No external Chef dependencies identified** - the Ansible playbooks use standard Ansible modules:
- **ansible.builtin.apt**: Standard package management (no replacement needed)
- **ansible.builtin.openssl_***: Certificate management modules (already Ansible native)
- **ansible.builtin.copy**: File management (already Ansible native)
- **ansible.builtin.service**: Service management (already Ansible native)

### Security Considerations

- **SSL/TLS Certificate Management**: Self-signed certificates are generated using Ansible's OpenSSL modules - production environments should integrate with proper CA or certificate management systems like Let's Encrypt
- **Hardcoded Credentials**: Chef server deployment scripts contain plaintext passwords and user credentials that should be moved to Ansible Vault or external secret management
- **SSH Security**: InSpec tests verify SSH root login restrictions and security configurations - these compliance checks should be maintained in the Ansible implementation
- **SSL Protocol Security**: POODLE vulnerability mitigation is already implemented via TLS 1.2 enforcement

### Technical Challenges

- **Test Kitchen Integration**: Current setup uses Test Kitchen with Vagrant for testing Ansible playbooks - consider migrating to Molecule for native Ansible testing workflows
- **InSpec Compliance Testing**: Chef InSpec tests provide compliance validation - evaluate whether to maintain InSpec or migrate to Ansible's built-in testing capabilities or other compliance frameworks
- **Chef Server Dependencies**: Deployment scripts install Chef Automate/Server infrastructure - determine if this Chef infrastructure is still needed or can be decommissioned

### Migration Order

1. **Ansible Playbooks** (already complete - no migration needed)
2. **InSpec Test Migration** (evaluate whether to keep InSpec or migrate to Ansible-native testing)
3. **Chef Infrastructure Decommission** (assess whether Chef Automate/Server is still required)

### Assumptions

- This repository serves as a demonstration/example rather than production infrastructure code
- The Ansible playbooks are already production-ready and follow Ansible best practices
- Chef InSpec is being used specifically for compliance testing rather than configuration management
- The Chef server deployment scripts may be supporting other Chef-managed infrastructure not visible in this repository
- Ubuntu 20.04 is the target platform, though playbooks may need updates for newer Ubuntu versions or RHEL-based systems
- Test Kitchen with Vagrant is acceptable for local development, or migration to Molecule is desired for better Ansible integration
- Self-signed certificates are acceptable for development/testing, but production deployment will require proper certificate management integration