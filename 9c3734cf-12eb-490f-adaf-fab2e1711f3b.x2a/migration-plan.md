# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and tools rather than traditional Chef cookbooks requiring migration. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration, Chef server deployment scripts, and compliance testing examples. The migration scope is minimal as most content is already Ansible-based or consists of deployment utilities.

## Module Migration Plan

This repository contains mixed technologies with limited Chef-specific infrastructure requiring migration:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Based on repository analysis, no traditional Chef cookbooks were found. The repository contains:

- **chef-and-ansible examples**:
    - Description: Ansible playbooks demonstrating Apache HTTPS configuration with Chef InSpec compliance testing
    - Path: chef-and-ansible/
    - Technology: Ansible (with Chef InSpec for testing)
    - Key Features: SSL certificate generation, Apache virtual host configuration, POODLE vulnerability mitigation, compliance verification

- **setup-automate deployment scripts**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server infrastructure
    - Path: setup-automate/
    - Technology: Bash shell scripts
    - Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `website_https.yml`: Ansible playbook for Apache HTTPS setup with SSL certificate management
- `poodle_fix.yml`: Ansible playbook for SSL protocol hardening (disables SSLv3, enables TLSv1.2)
- `deploy-automate.sh`: Chef Automate and Infra Server deployment automation script
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL configuration
- `ssh_profile.rb`: InSpec security profile for SSH root login compliance (STIG-based)

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml), with RHEL compatibility implied by STIG references
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for testing)
- **Cloud Platform**: Not specified, designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Already integrated with Ansible playbooks for compliance testing - no migration needed
- **Test Kitchen**: Currently configured for Ansible playbook testing - can be retained or replaced with molecule
- **OpenSSL Ansible modules**: Already using python3-openssl package and openssl_* modules - no changes required
- **Apache2 package**: Pinned to specific version (2.4.41-4ubuntu3.10) - may need version updates for target environment

### Security Considerations

- **SSL/TLS Configuration**: Existing playbooks implement proper SSL hardening (disables SSLv3, enforces TLSv1.2)
- **Self-signed certificates**: Current implementation uses self-signed certificates - consider certificate authority integration for production
- **SSH hardening**: InSpec profiles enforce STIG compliance for SSH root login restrictions
- **Credential management**: Deployment scripts contain hardcoded credentials that should be externalized to Ansible Vault:
  - Chef server admin passwords
  - User email addresses
  - Organization names
  - Certificate passphrases (if any)

### Technical Challenges

- **Testing framework transition**: Current Test Kitchen + InSpec setup works well - migration challenge is minimal
- **Chef server dependency**: Deployment scripts assume Chef infrastructure needs - evaluate if Chef Automate/Server still required in pure Ansible environment
- **Compliance integration**: InSpec profiles provide STIG compliance verification - ensure equivalent Ansible compliance tooling if removing Chef InSpec
- **Certificate management**: Self-signed certificate approach may need enhancement for production environments

### Migration Order

1. **Ansible playbooks** (already complete - no migration needed)
2. **InSpec compliance tests** (evaluate retention vs. replacement with ansible-lint/molecule)
3. **Deployment scripts** (convert to Ansible playbooks if Chef infrastructure still needed)

### Assumptions

- The repository serves as examples/documentation rather than production infrastructure requiring migration
- Chef InSpec integration with Ansible is intentional and may be retained for compliance testing
- Chef server deployment scripts may become obsolete if migrating to pure Ansible infrastructure
- SSL certificate management approach (self-signed) is acceptable for demonstration purposes
- Ubuntu 20.04 target platform is still current for migration timeline
- Test Kitchen configuration suggests development/testing workflow that may need adaptation
- STIG compliance requirements (referenced in ssh_profile.rb) must be maintained in migrated solution
- Hardcoded credentials in deployment scripts are acceptable for example purposes but require Ansible Vault integration for production use