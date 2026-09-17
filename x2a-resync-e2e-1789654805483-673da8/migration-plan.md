# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible for compliance automation. **No actual migration is required** as the repository already uses Ansible playbooks as the primary automation technology. The Chef InSpec components serve as compliance testing tools that complement the existing Ansible infrastructure.

## Module Migration Plan

This repository contains demonstration examples rather than production infrastructure modules:

### MODULE INVENTORY

**No Chef cookbooks or modules requiring migration were found.** The repository contains:

- **website-https-demo**:
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates and SSL security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already target technology)
    - Key Features: Apache 2.4.41 installation, SSL certificate generation, virtual host configuration, security compliance

- **poodle-fix-demo**:
    - Description: Ansible playbook demonstrating SSL protocol hardening to address POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already target technology)
    - Key Features: SSL protocol restriction to TLS 1.2, Apache configuration updates

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL configuration
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security hardening (STIG controls)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static web content for testing

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured as Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

**No migration dependencies** - the repository already uses Ansible. However, for compliance testing:

- **Chef InSpec**: Continue using InSpec for compliance verification alongside Ansible, or migrate to:
  - Ansible's built-in `assert` module for simple checks
  - Testinfra for Python-based infrastructure testing
  - Goss for YAML-based system validation

### Security Considerations

The existing Ansible playbooks demonstrate good security practices:
- **SSL/TLS Configuration**: Self-signed certificate generation with proper file permissions (0640 for certs directory)
- **Protocol Hardening**: POODLE vulnerability mitigation by restricting to TLS 1.2
- **SSH Security**: InSpec profile includes STIG-compliant SSH root login restrictions
- **File Permissions**: Appropriate ownership and permissions for web content (0644) and configuration files (0640)

**Vault/secrets management**: 
- Current implementation uses hardcoded values in playbook variables
- Consider migrating to Ansible Vault for sensitive data like certificates and passwords
- No encrypted data bags or Chef Vault usage detected

### Technical Challenges

**Minimal challenges** as this is primarily a demonstration repository:

- **InSpec Integration**: If continuing to use InSpec for compliance testing, maintain the existing Test Kitchen + InSpec workflow
- **Certificate Management**: Current self-signed certificate approach is suitable for testing but production environments should integrate with proper CA or Let's Encrypt
- **Hardcoded Values**: Playbook variables should be externalized to inventory or group_vars for production use

### Migration Order

**No migration required** - repository is already Ansible-based. For enhancement:

1. **Immediate**: Continue using existing Ansible playbooks as-is
2. **Short-term**: Externalize hardcoded variables to Ansible inventory
3. **Long-term**: Consider replacing InSpec with native Ansible testing if desired

### Assumptions

- This repository serves as a demonstration/example rather than production infrastructure
- The Chef components (InSpec tests, Automate deployment scripts) are intentionally preserved to show integration patterns
- No actual Chef cookbooks or recipes exist that require migration to Ansible
- The target audience includes teams evaluating Chef InSpec alongside Ansible for compliance automation
- Test Kitchen with Vagrant is used for local development and testing workflows
- Ubuntu 20.04 is the target platform based on the kitchen.yml configuration
- The Apache version (2.4.41-4ubuntu3.10) is specifically pinned for consistency in testing environments