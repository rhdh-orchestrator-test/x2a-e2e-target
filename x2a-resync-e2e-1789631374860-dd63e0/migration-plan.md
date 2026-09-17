# MIGRATION FROM MIXED ANSIBLE/CHEF INSPEC TO ANSIBLE

This repository contains example Ansible playbooks with Chef InSpec compliance testing and Chef infrastructure deployment scripts. **This is not a traditional migration scenario** - the repository already contains Ansible playbooks and serves as a demonstration of using Chef InSpec alongside Ansible for compliance automation. The migration focus should be on standardizing to pure Ansible solutions and replacing Chef InSpec with Ansible-native compliance tools.

## Module Migration Plan

This repository contains demonstration code and deployment scripts rather than production modules:

### MODULE INVENTORY

**website-https-demo**:
- Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS security hardening, and virtual host setup
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

**poodle-fix-demo**:
- Description: Ansible playbook demonstrating SSL/TLS protocol hardening to address POODLE vulnerability by disabling SSLv3 and enforcing TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL configuration replacement, protocol restriction, service restart handling

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Ansible provisioner with InSpec verifier for compliance testing
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality, SSL protocol validation, and port verification
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec security compliance test for SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server infrastructure
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying standalone Chef Infra Server
- `chef-and-ansible/index.html`: Static HTML test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native compliance solutions such as:
  - `ansible.posix.firewalld` for port verification
  - `uri` module for HTTP/HTTPS endpoint testing  
  - `openssl_certificate_info` for SSL certificate validation
  - Custom Ansible tasks using `shell` module for protocol testing
- **Test Kitchen with Vagrant**: Replace with Ansible Molecule for testing and validation
- **Chef Automate/Server deployment**: Replace with Ansible AWX/Tower or native Ansible automation platform

### Security Considerations

- **SSL/TLS Configuration Management**: Current playbooks handle certificate generation and SSL hardening - ensure Ansible Vault integration for certificate management in production
- **SSH Security Compliance**: InSpec test validates SSH root login restrictions - implement equivalent Ansible tasks with `lineinfile` module for sshd_config management
- **Hardcoded Credentials**: Deployment scripts contain plaintext passwords and user credentials - migrate to Ansible Vault for secrets management
- **Certificate Management**: Self-signed certificates used in demo - plan integration with proper CA or Let's Encrypt for production environments

### Technical Challenges

- **InSpec Test Translation**: Convert Chef InSpec compliance tests to Ansible-native validation tasks or integrate with external compliance tools like OpenSCAP
- **Test Kitchen Replacement**: Migrate testing workflow from Test Kitchen to Ansible Molecule for consistent testing methodology
- **Infrastructure Deployment**: Replace bash-based Chef infrastructure deployment with Ansible playbooks for infrastructure provisioning
- **Compliance Reporting**: Establish equivalent compliance reporting mechanism to replace Chef InSpec's structured output format

### Migration Order

1. **Infrastructure Deployment Scripts** (low complexity, high value)
   - Convert bash deployment scripts to Ansible playbooks
   - Implement proper secrets management with Ansible Vault
   
2. **Compliance Test Migration** (moderate complexity)
   - Translate InSpec tests to Ansible verification tasks
   - Implement Molecule testing framework
   
3. **Testing Framework Standardization** (high complexity, dependencies)
   - Complete migration from Test Kitchen to Molecule
   - Establish CI/CD pipeline integration with pure Ansible toolchain

### Assumptions

- The repository serves as demonstration/example code rather than production infrastructure requiring migration
- Target environment will maintain Ubuntu/Debian-based systems as indicated by apt package manager usage
- Current Ansible playbooks are already functional and represent the desired end state for configuration management
- Chef InSpec compliance testing needs replacement with Ansible-native solutions rather than maintaining hybrid toolchain
- Test Kitchen usage indicates development/testing workflow that should be standardized to Ansible Molecule
- Deployment scripts represent one-time infrastructure setup rather than ongoing configuration management
- SSL certificate management will transition from self-signed certificates to proper certificate authority integration
- SSH security compliance requirements will remain consistent with current STIG-based validation approach