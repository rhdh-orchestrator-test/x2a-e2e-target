# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and deployment scripts rather than production Chef cookbooks requiring migration. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration for compliance automation, along with Chef server deployment scripts. This represents a minimal migration effort focused on consolidating example code and deployment automation.

## Module Migration Plan

This repository contains demonstration and deployment scripts rather than production Chef modules:

### MODULE INVENTORY

**No Chef cookbooks or modules found for migration.** This repository contains:

- **chef-and-ansible examples**: Ansible playbooks demonstrating Chef InSpec integration for compliance testing
- **setup-automate scripts**: Bash deployment scripts for Chef Automate and Chef Infra Server installation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Ansible provisioner with InSpec verifier for testing compliance automation workflows
- `chef-and-ansible/website_https.yml`: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates and SSL hardening
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL protocol hardening (disabling SSLv3, enabling TLSv1.2)
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec compliance tests verifying HTTPS functionality and SSL protocol configuration
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec compliance profile testing SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Bash script for automated Chef Automate and Chef Infra Server deployment
- `setup-automate/deploy-chef-server.sh`: Bash script for standalone Chef Infra Server deployment

### Target Details

- **Operating System**: Ubuntu 20.04 (based on kitchen.yml platform specification and Apache package versions)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Already integrated with Ansible in existing examples - no migration required
- **Test Kitchen**: Currently configured for Ansible provisioner - can be retained or replaced with molecule for Ansible-native testing
- **Apache 2.4.41**: Specific package version pinned in playbook - verify availability in target environment

### Security Considerations

- **Self-signed certificates**: Current implementation generates self-signed SSL certificates - consider integration with proper CA or Let's Encrypt for production use
- **Hardcoded credentials**: Deployment scripts contain plaintext passwords and user details - migrate to Ansible Vault or external secret management
- **SSL/TLS configuration**: Existing SSL hardening (TLSv1.2 enforcement, SSLv3 disabling) should be maintained in consolidated Ansible roles
- **STIG compliance**: SSH hardening profiles already implemented in InSpec - ensure equivalent Ansible hardening roles maintain compliance standards

### Technical Challenges

- **InSpec integration**: Existing Chef InSpec tests provide compliance validation - ensure continued InSpec support in pure Ansible environment or migrate to Ansible compliance modules
- **Test Kitchen replacement**: Consider migrating from Test Kitchen to Molecule for Ansible-native testing workflows
- **Deployment script consolidation**: Bash deployment scripts should be converted to Ansible playbooks for consistency and idempotency

### Migration Order

1. **Consolidate Ansible playbooks** (low risk, immediate value) - organize existing playbooks into proper role structure
2. **Convert deployment scripts** (moderate complexity) - migrate bash scripts to Ansible playbooks with proper secret management
3. **Migrate testing framework** (low risk) - evaluate Test Kitchen vs Molecule for Ansible testing

### Assumptions

- Repository serves as example/demonstration code rather than production infrastructure requiring migration
- Existing Ansible playbooks are already functional and represent the desired end state
- Chef InSpec will continue to be used for compliance testing alongside Ansible
- Target environment supports the specific Apache package versions currently pinned in playbooks
- Current SSL certificate generation approach (self-signed) is acceptable for demonstration purposes
- Deployment scripts are used for lab/development environments rather than production Chef server deployments