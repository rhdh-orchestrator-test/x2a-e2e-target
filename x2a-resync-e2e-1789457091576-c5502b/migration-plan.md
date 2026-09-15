# MIGRATION FROM CHEF TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible rather than traditional Chef cookbooks requiring migration. The content is already primarily Ansible-based with InSpec compliance testing. **No actual migration is required** - this is a demonstration/example repository showing how to use Chef InSpec alongside Ansible for compliance automation.

## Module Migration Plan

This repository contains demonstration code and deployment scripts rather than production Chef modules:

### MODULE INVENTORY

**No Chef modules found for migration.** This repository contains:

- **website_https**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS setup, and virtual host configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host setup, SSL module activation

- **poodle_fix**:
    - Description: Ansible playbook demonstrating SSL protocol hardening by disabling SSLv3 and enforcing TLS 1.2 to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL configuration hardening, protocol restriction, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests verifying HTTPS functionality, SSL protocols, and web service availability
- `tests/ssh_profile.rb`: InSpec compliance profile testing SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for demonstration environment
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test page for web server verification

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address

**No external Chef dependencies to migrate** - this repository demonstrates:
- **apache2 (2.4.41-4ubuntu3.10)**: Already managed via Ansible apt module
- **openssl/python3-openssl**: Certificate management handled by Ansible openssl modules
- **Chef InSpec**: Retained for compliance testing alongside Ansible automation

### Security Considerations

**Existing security practices already implemented in Ansible:**
- SSL/TLS certificate management: Self-signed certificates generated via Ansible openssl modules
- Protocol hardening: TLS 1.2 enforcement, SSLv3 disabled via configuration management
- SSH security: InSpec tests verify PermitRootLogin restrictions and STIG compliance
- File permissions: Proper ownership and permissions set on certificates (0640) and web content (0644/0755)

### Technical Challenges

**No migration challenges - repository is already Ansible-based:**
- Challenge 1: Understanding repository purpose - This is a demonstration repository, not production code requiring migration
- Challenge 2: InSpec integration - Already properly configured with Test Kitchen for Ansible playbook testing
- Challenge 3: Deployment scripts - Bash scripts for Chef server deployment are for demo environment setup, not production automation

### Migration Order

**No migration required** - recommended actions:
1. Review and adapt Ansible playbooks for production use (remove hardcoded values, add proper variable management)
2. Enhance InSpec compliance profiles for organizational security requirements
3. Integrate with production CI/CD pipelines if adopting this compliance testing approach

### Assumptions

- This repository serves as example/demonstration code rather than production infrastructure requiring migration
- The Chef components (Automate/Infra Server deployment scripts) are for setting up demonstration environments, not production Chef infrastructure
- InSpec compliance testing framework will be retained alongside Ansible for continuous compliance validation
- Test Kitchen configuration suggests this is used for local development and testing of the Ansible + InSpec integration pattern
- Ubuntu 20.04 target platform may need updating for production use (current LTS is 22.04)
- Self-signed certificates are acceptable for demonstration purposes but would need proper CA-signed certificates in production
- The hardcoded credentials and configuration values in deployment scripts are for demo purposes only