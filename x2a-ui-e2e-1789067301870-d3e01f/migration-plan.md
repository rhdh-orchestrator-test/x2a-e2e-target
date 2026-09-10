# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible rather than production Chef infrastructure requiring migration. The content is primarily educational/demonstration material showing how to use InSpec for compliance testing alongside Ansible playbooks. **No actual migration is required** as the Ansible playbooks are already in their target state.

## Module Migration Plan

This repository contains demonstration content rather than production modules requiring migration:

### MODULE INVENTORY

**No Chef cookbooks or modules found for migration.** This repository contains:

- **website_https**: 
  - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS security hardening, and virtual host setup
  - Path: chef-and-ansible/website_https.yml
  - Technology: Ansible (already target state)
  - Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

- **poodle_fix**:
  - Description: Ansible playbook demonstrating SSL protocol hardening to disable SSLv3 and enforce TLS 1.2 (POODLE vulnerability mitigation)
  - Path: chef-and-ansible/poodle_fix.yml
  - Technology: Ansible (already target state)
  - Key Features: Apache SSL configuration replacement, TLS protocol enforcement, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant and InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests verifying HTTPS functionality, SSL protocols, and web service availability
- `tests/ssh_profile.rb`: InSpec security profile testing SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for demonstration environment
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test content for web server verification

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for local development/testing environments

## Migration Approach

### Key Dependencies to Address

**No external dependencies requiring migration** - the Ansible content uses standard modules:
- **apache2 (2.4.41-4ubuntu3.10)**: Already specified with exact version in playbook
- **openssl/python3-openssl**: Standard SSL certificate management tools, already configured
- **Test Kitchen with InSpec**: Testing framework already configured for Ansible playbook validation

### Security Considerations

The existing Ansible playbooks already implement security best practices:
- **SSL/TLS Configuration**: TLS 1.2 enforcement, SSLv3 disabled (POODLE mitigation)
- **Certificate Management**: Self-signed certificate generation with proper file permissions (0640 for certs directory)
- **SSH Hardening**: InSpec tests verify SSH root login restrictions per STIG requirements
- **File Permissions**: Proper ownership and permissions for web content (0644) and configuration files (0640)
- **Service Management**: Proper handler configuration for secure service restarts

### Technical Challenges

**No migration challenges** - this is demonstration content showing:
- How to integrate Chef InSpec with Ansible for compliance automation
- Best practices for SSL/TLS configuration in Ansible
- Test-driven infrastructure development with Test Kitchen and InSpec
- Security compliance testing patterns

### Migration Order

**No migration required** - content is already in target state. For teams wanting to adopt this pattern:

1. Review existing Ansible playbooks for compliance testing integration opportunities
2. Implement InSpec test profiles for security requirements
3. Configure Test Kitchen for automated testing workflows
4. Deploy Chef Automate/InSpec infrastructure if centralized compliance reporting is needed

### Assumptions

- This repository serves as educational/reference material rather than production infrastructure
- Teams may want to extract the Ansible playbooks and InSpec tests as templates for their own infrastructure
- The Chef Automate deployment scripts are for setting up compliance reporting infrastructure, not for migration
- The demonstration focuses on Ubuntu/Debian systems but patterns are applicable to other Linux distributions
- SSL certificate management shown uses self-signed certificates appropriate for testing but would need CA-signed certificates for production use