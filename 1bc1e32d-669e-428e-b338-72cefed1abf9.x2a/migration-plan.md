# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository is a demonstration project showing Chef InSpec integration with Ansible for compliance automation. The migration scope is minimal as the infrastructure automation is already implemented in Ansible. The primary migration task involves replacing Chef InSpec compliance testing with native Ansible testing solutions.

## Module Migration Plan

This repository contains demonstration content that combines Ansible playbooks with Chef InSpec testing:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths have been verified using directory listing and file search tools.

- **website-https-deployment**:
    - Description: Apache web server deployment with SSL/TLS configuration, self-signed certificate generation, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

- **poodle-vulnerability-fix**:
    - Description: SSL protocol hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration remediation, protocol restriction, service restart handling

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `chef-and-ansible/index.html`: Static HTML test content for web server validation
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG control)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for demonstration environment
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible native testing modules (ansible.builtin.uri, ansible.builtin.service_facts, ansible.posix.firewalld_info)
- **Test Kitchen**: Replace with molecule for Ansible role testing and validation
- **Chef Automate/Server**: Remove dependency as this is demonstration infrastructure only

### Security Considerations

- **SSL/TLS Certificate Management**: Current implementation uses self-signed certificates generated via OpenSSL. Migration should consider:
  - Implementing proper certificate lifecycle management
  - Integration with Let's Encrypt or internal CA
  - Certificate rotation and renewal automation
- **SSH Security Hardening**: InSpec test validates SSH root login restrictions. Ansible equivalent should use:
  - ansible.builtin.lineinfile module for sshd_config validation
  - ansible.builtin.service module for SSH service state verification
- **Vault/secrets management**: 
  - No encrypted secrets detected in current implementation
  - Hardcoded credentials present in setup scripts (userpassword='password')
  - SSL private keys generated at runtime without secure storage

### Technical Challenges

- **InSpec to Ansible Testing Migration**: 
  - Current InSpec tests validate port listening (443), HTTP response codes, SSL protocol support
  - Ansible equivalent requires combination of ansible.builtin.uri, ansible.builtin.wait_for, and custom validation tasks
  - SSL protocol testing complexity increases without InSpec's built-in SSL resource
- **Test Kitchen Replacement**: 
  - Current workflow uses Vagrant + Test Kitchen + InSpec
  - Migration to Molecule requires restructuring test scenarios and verification methods
- **Compliance Framework Integration**:
  - Current SSH test references STIG controls (RHEL-08-000227, SRG-OS-000112)
  - Ansible testing needs to maintain compliance traceability and reporting

### Migration Order

1. **website-https-deployment** (Priority 1: Already Ansible, minimal changes needed)
   - Convert InSpec tests to Ansible verification tasks
   - Implement proper certificate management
   - Add comprehensive error handling

2. **poodle-vulnerability-fix** (Priority 2: Simple SSL hardening, low complexity)
   - Enhance with additional SSL/TLS security configurations
   - Add validation tasks for protocol restrictions
   - Implement idempotency checks

3. **Testing Infrastructure** (Priority 3: Complex testing framework migration)
   - Replace Test Kitchen with Molecule
   - Convert InSpec compliance tests to Ansible verification
   - Maintain STIG compliance reporting capabilities

### Assumptions

- The repository serves as a demonstration/proof-of-concept rather than production infrastructure
- Chef Automate/Server deployment scripts are for lab environment setup only and not intended for production migration
- Target environment will continue to use Ubuntu/Debian-based systems (apt package manager dependencies)
- SSL certificate requirements will evolve from self-signed to proper CA-issued certificates
- Compliance testing framework (STIG controls) must be maintained in the migrated solution
- Test Kitchen workflow will be replaced with Molecule for consistency with Ansible ecosystem
- Current hardcoded credentials in setup scripts indicate this is demonstration code only
- SSH hardening requirements follow RHEL STIG guidelines despite Ubuntu target platform
- Apache web server will remain the target web server technology (no migration to Nginx or other alternatives)
- Vagrant-based local testing environment will be maintained for development workflows