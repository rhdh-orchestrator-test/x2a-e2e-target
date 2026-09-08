# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains educational examples demonstrating Chef InSpec integration with Ansible for compliance automation. The migration scope is minimal as the primary automation is already implemented in Ansible playbooks. The main consideration is replacing Chef InSpec testing with native Ansible testing approaches.

## Module Migration Plan

This repository contains demonstration code rather than production Chef cookbooks requiring migration. The existing Ansible playbooks serve as reference implementations that are already migration-ready:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Apache HTTPS web server configuration with SSL certificate generation, virtual host setup, and POODLE vulnerability remediation
- Path: chef-and-ansible/
- Technology: Ansible (with Chef InSpec for testing)
- Key Features: Self-signed SSL certificates, Apache virtual host configuration, SSL protocol hardening, compliance verification

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration using Vagrant driver with Ansible provisioner and InSpec verifier
- `website_https.yml`: Ansible playbook for Apache HTTPS setup with SSL certificate generation and virtual host configuration
- `poodle_fix.yml`: Ansible playbook for SSL protocol hardening to address POODLE vulnerability
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL configuration
- `tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible native testing using ansible-test, molecule, or testinfra
- **Test Kitchen**: Replace with Molecule for Ansible role testing and validation
- **Vagrant**: Continue using for local development, or migrate to container-based testing

### Security Considerations

- **SSL Certificate Management**: Current implementation uses self-signed certificates generated via OpenSSL Ansible modules - production environments should integrate with proper CA or certificate management solutions
- **SSH Hardening**: InSpec profile validates SSH root login restrictions - migrate compliance checks to Ansible assert tasks or dedicated security roles
- **Apache Security**: SSL protocol configuration addresses POODLE vulnerability - ensure continued security hardening in migrated playbooks
- **Credential Management**: Deployment scripts contain hardcoded credentials (usernames, passwords, email addresses) - implement Ansible Vault for secrets management

### Technical Challenges

- **Testing Framework Migration**: Replace Chef InSpec compliance tests with Ansible-native testing approaches (testinfra, molecule, or custom assert tasks)
- **Compliance Validation**: Maintain security compliance verification capabilities without InSpec dependency
- **Test Kitchen Replacement**: Migrate from Test Kitchen to Molecule for comprehensive Ansible testing workflows
- **Documentation Updates**: Update examples to reflect pure Ansible approach rather than Chef InSpec integration

### Migration Order

1. **Apache HTTPS Playbook** (low risk, already Ansible-native)
2. **SSL Hardening Playbook** (moderate complexity, security-focused)
3. **Testing Framework** (high complexity, requires new tooling decisions)

### Assumptions

- This repository serves as educational/demonstration content rather than production infrastructure requiring migration
- The existing Ansible playbooks are already well-structured and follow best practices
- Test Kitchen and InSpec dependencies are acceptable to remove in favor of Ansible-native testing
- The target audience is familiar with Ansible testing frameworks like Molecule or testinfra
- Chef Automate deployment scripts are reference implementations and not production deployment requirements
- SSL certificate generation approach (self-signed) is appropriate for demonstration purposes but would need enhancement for production use
- Ubuntu package versions specified in playbooks may need updates for current security patches
- SSH compliance requirements remain consistent with existing InSpec profile specifications