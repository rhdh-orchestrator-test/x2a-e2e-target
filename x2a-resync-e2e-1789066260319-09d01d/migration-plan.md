# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and documentation rather than production Chef cookbooks requiring migration. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration, deployment scripts for Chef infrastructure, and educational materials. The migration scope is minimal as the repository already contains Ansible content and supporting materials.

## Module Migration Plan

This repository contains demonstration and setup materials rather than production Chef modules:

### MODULE INVENTORY

**No Chef cookbooks or modules found for migration.** This repository contains:

- **chef-and-ansible examples**: Ansible playbooks demonstrating Chef InSpec integration for compliance automation
- **setup-automate scripts**: Bash deployment scripts for Chef Automate and Chef Infra Server infrastructure

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for Apache HTTPS configuration with SSL certificate generation
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL protocol hardening (disables SSLv3, enables TLS 1.2)
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Ansible provisioner and InSpec verifier
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security control for SSH root login restrictions
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server standalone deployment script

### Target Details

Based on the Ansible playbooks and deployment scripts:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml), with RHEL compatibility indicated in InSpec controls
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for testing)
- **Cloud Platform**: Cloud-agnostic deployment scripts support on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Already integrated with Ansible via Test Kitchen configuration - no migration needed
- **Apache 2.4.41**: Managed via Ansible apt module - already migrated
- **OpenSSL/PyOpenSSL**: Certificate management handled by Ansible openssl modules - already migrated
- **Chef Automate/Infra Server**: Deployment scripts for Chef infrastructure - consider Ansible Tower/AWX as alternative

### Security Considerations

- **SSL/TLS Configuration**: Ansible playbooks demonstrate proper SSL hardening practices:
  - Self-signed certificate generation via Ansible openssl modules
  - SSL protocol restrictions (TLS 1.2 only, SSLv3 disabled)
  - InSpec verification of SSL configuration compliance
- **SSH Hardening**: InSpec controls verify SSH root login restrictions (STIG compliance)
- **Certificate Management**: Self-signed certificates used for demonstration - production environments should integrate with proper CA or Let's Encrypt
- **Credential Patterns**: Hardcoded credentials in deployment scripts (userpassword='password') - requires vault integration for production use

### Technical Challenges

- **No actual migration required**: Repository contains examples and documentation rather than production Chef code
- **InSpec Integration**: Existing Test Kitchen configuration successfully integrates Ansible provisioning with InSpec verification
- **Chef Infrastructure Dependencies**: Organizations using these deployment scripts may need to migrate from Chef Automate to Ansible Tower/AWX for centralized automation management

### Migration Order

1. **Documentation Review** (immediate): Update README files to reflect Ansible-first approach
2. **Example Enhancement** (low priority): Expand Ansible examples to demonstrate additional compliance scenarios
3. **Infrastructure Migration** (if applicable): For organizations using the Chef deployment scripts, plan migration to Ansible Tower/AWX

### Assumptions

- This repository serves as educational/demonstration material rather than production infrastructure code
- Organizations referencing these examples may have separate Chef cookbooks requiring actual migration
- The Ansible playbooks represent target state examples rather than source code requiring migration
- InSpec integration patterns demonstrated here are intended for compliance automation alongside Ansible
- Deployment scripts are used for Chef infrastructure setup rather than application deployment automation
- SSL certificate generation is for demonstration purposes - production environments require proper certificate authority integration
- SSH hardening controls assume RHEL/CentOS environments based on STIG references, though Ubuntu compatibility is maintained