# MIGRATION FROM ANSIBLE TO ANSIBLE (MODERNIZATION)

This repository contains Ansible playbooks and Chef InSpec compliance tests that demonstrate integration between Ansible automation and Chef InSpec compliance validation. The migration scope is actually a **modernization effort** rather than a technology migration, as the core automation is already implemented in Ansible. The focus should be on updating deprecated syntax, improving security practices, and enhancing the existing Ansible implementation.

**Timeline Estimate**: 1-2 weeks for modernization
**Complexity**: Low to Medium (existing Ansible code needs updates, not full rewrite)
**Team Coordination**: Minimal - single developer can handle modernization

## Module Migration Plan

This repository contains Ansible playbooks and supporting infrastructure that need modernization and security improvements:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths have been verified using directory listing and file search tools.

- **website-https-deployment**:
    - Description: Apache web server deployment with SSL/TLS configuration, self-signed certificate generation, and virtual host setup for a "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (needs modernization)
    - Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

- **poodle-ssl-fix**:
    - Description: Security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2 to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (needs modernization)
    - Key Features: SSL protocol configuration, Apache SSL module hardening, service restart handlers

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance (STIG control)
- `chef-and-ansible/index.html`: Static HTML test file for web server validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen for local development and testing)
- **Cloud Platform**: Not specified (designed for on-premises or cloud VM deployment)

## Migration Approach

### Key Dependencies to Address
- **apache2=2.4.41-4ubuntu3.10**: Update to latest security-patched version using package state management
- **python3-openssl**: Replace with community.crypto collection for certificate management
- **Test Kitchen with Vagrant**: Consider migration to molecule for Ansible-native testing
- **Chef InSpec**: Maintain for compliance validation - no migration needed

### Security Considerations
- **Hardcoded package versions**: The playbook pins Apache to a specific version (2.4.41-4ubuntu3.10) which may have security vulnerabilities
- **Self-signed certificates**: Current implementation uses self-signed certificates - consider Let's Encrypt integration for production
- **Credential management**: Deployment scripts contain hardcoded passwords and usernames that should be externalized
- **SSL/TLS configuration**: POODLE fix is present but should be expanded to include modern TLS best practices
- **Vault/secrets management**: 
  - 2 hardcoded credentials detected in setup scripts (username/password combinations)
  - SSL certificate and key files generated without proper secret management
  - No Ansible Vault usage detected - should be implemented for sensitive data

### Technical Challenges
- **Deprecated Ansible syntax**: Playbooks use older syntax patterns that should be modernized
- **Handler naming inconsistency**: Handler names don't match between tasks and handler definitions
- **Package management**: Fixed package versions may cause compatibility issues on newer systems
- **Certificate management**: Self-signed certificate generation should be replaced with proper CA or Let's Encrypt
- **Test integration**: InSpec tests are valuable but integration with modern CI/CD pipelines needs consideration

### Migration Order
1. **website-https-deployment** (modernize syntax, update packages, improve security)
2. **poodle-ssl-fix** (expand SSL hardening, add modern TLS configurations)
3. **Infrastructure modernization** (update Test Kitchen to Molecule, implement Ansible Vault)

### Assumptions
- The target environment will remain Ubuntu-based but may need to support newer LTS versions
- InSpec compliance testing should be retained as it provides valuable security validation
- The Chef Automate deployment scripts are for development/demo purposes and may not need migration
- SSL certificate requirements may change from self-signed to proper CA-issued certificates in production
- The current Test Kitchen + Vagrant setup is acceptable for development but may need CI/CD integration
- Package versions should be updated to latest stable releases rather than pinned versions
- The existing Apache configuration approach is acceptable but may benefit from template-based management
- SSH hardening requirements (from InSpec profile) should be expanded beyond just root login restrictions
- The current handler restart approach may need refinement for zero-downtime deployments