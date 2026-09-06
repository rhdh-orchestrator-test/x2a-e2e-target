# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and demonstration materials that showcase integration between Chef InSpec and Ansible for compliance automation. The migration scope is limited as this is primarily a demonstration/example repository rather than production infrastructure code. The repository contains existing Ansible playbooks with Chef InSpec verification tests, making this more of a consolidation effort than a full technology migration.

**Timeline Estimate**: 1-2 weeks
**Complexity**: Low to Medium
**Risk Level**: Low (demonstration code, not production infrastructure)

## Module Migration Plan

This repository contains demonstration materials and example configurations that showcase Chef InSpec integration with Ansible:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths have been verified using directory listing and file search tools.

- **website-https-demo**:
    - Description: Apache HTTPS website deployment with SSL certificate generation, virtual host configuration, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: Self-signed SSL certificates, Apache virtual host setup, security configuration, InSpec compliance testing

- **poodle-ssl-fix**:
    - Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL protocol configuration, POODLE vulnerability mitigation, service restart handling

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with Vagrant driver and InSpec verifier
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS website functionality and SSL configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance verification
- `chef-and-ansible/index.html`: Static HTML test file for website deployment verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for lab environments
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

- **apache2 (2.4.41-4ubuntu3.10)**: Already properly managed via Ansible apt module with version pinning
- **openssl**: Used for SSL certificate generation, already handled by Ansible openssl modules
- **python3-openssl**: Required for Ansible SSL certificate modules, already included in playbook
- **Test Kitchen**: Testing framework integration remains unchanged
- **Chef InSpec**: Compliance testing tool, no migration needed as it integrates with Ansible

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates are generated using Ansible openssl modules with proper file permissions (0640 for private keys)
- **Apache Security Configuration**: SSL protocol hardening implemented to disable vulnerable protocols and enforce TLS 1.2
- **SSH Security Profile**: InSpec tests verify SSH root login is disabled per security compliance requirements
- **Vault/secrets management**: 
  - No encrypted data bags or Chef Vault usage detected
  - Hardcoded credentials found in setup scripts (userpassword='password') - 2 instances in setup-automate directory
  - SSL certificate paths and configuration are properly templated
  - No environment variable secrets detected
  - Total credentials requiring attention: 2 hardcoded passwords in deployment scripts

### Technical Challenges

- **Test Integration Complexity**: The repository demonstrates Chef InSpec integration with Ansible, which is already the target state - no migration needed for this integration
- **Documentation Updates**: README files reference Chef-specific terminology and may need updates to reflect pure Ansible approach if Chef InSpec integration is removed
- **Deployment Script Dependencies**: Setup scripts install Chef Automate/Server which may not be needed in pure Ansible environment

### Migration Order

1. **Setup Scripts Review** (Priority 1): Evaluate whether Chef Automate/Server deployment scripts are still needed
2. **Documentation Updates** (Priority 2): Update README files and comments to reflect current Ansible-centric approach
3. **Security Hardening** (Priority 3): Replace hardcoded credentials in deployment scripts with proper secret management

### Assumptions

- The primary purpose of this repository is to demonstrate Chef InSpec integration with Ansible, which is already achieved
- The existing Ansible playbooks are functional and follow best practices
- Test Kitchen integration with InSpec will be maintained for compliance verification
- The Ubuntu 20.04 target platform will remain the same
- Local development/testing environment setup will continue using Vagrant
- Chef Automate/Server deployment scripts may be retained for demonstration purposes
- The repository serves as educational/example content rather than production infrastructure
- InSpec compliance tests provide value and should be retained regardless of the underlying configuration management tool
- The SSL certificate generation approach using self-signed certificates is acceptable for demonstration purposes
- Apache version pinning (2.4.41-4ubuntu3.10) is intentional for reproducible testing environments