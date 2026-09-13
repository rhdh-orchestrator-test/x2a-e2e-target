# MIGRATION FROM MIXED CHEF/ANSIBLE TO ANSIBLE

This repository is a demonstration/example repository that showcases using Chef InSpec for compliance testing alongside Ansible playbooks. The migration scope is minimal as the primary automation is already implemented in Ansible. The main migration task involves replacing Chef InSpec tests with native Ansible testing approaches and removing Chef server deployment dependencies.

**Migration Complexity**: Low  
**Estimated Timeline**: 1-2 weeks  
**Primary Challenge**: Replacing Chef InSpec compliance tests with Ansible-native testing solutions

## Module Migration Plan

This repository contains mixed technologies with Ansible playbooks already present and Chef InSpec tests that need migration:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server deployment with HTTPS/SSL configuration, self-signed certificate generation, and virtual host setup
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, directory structure creation

**ssl-security-hardening**:
- Description: SSL/TLS security hardening playbook that disables SSLv3 and enforces TLS 1.2 to mitigate POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, POODLE vulnerability mitigation, service restart handling

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with InSpec verification - needs migration to molecule or native Ansible testing
- `chef-and-ansible/index.html`: Static HTML test content for web server verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script - can be removed post-migration
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script - can be removed post-migration

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for local development/testing environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible native testing using `ansible.builtin.uri`, `ansible.builtin.wait_for`, and `ansible.builtin.assert` modules
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and verification
- **Chef Server/Automate**: Remove deployment scripts as they are no longer needed in pure Ansible environment

### Security Considerations

- **SSL Certificate Management**: Current implementation uses self-signed certificates generated via OpenSSL Ansible modules - consider migration to Let's Encrypt or proper CA-signed certificates for production
- **Hardcoded Credentials**: Chef server deployment scripts contain hardcoded usernames, passwords, and email addresses that should be externalized to Ansible Vault
- **SSH Security**: InSpec tests verify SSH root login is disabled - migrate these compliance checks to Ansible assertions
- **SSL/TLS Configuration**: POODLE vulnerability mitigation is already implemented in Ansible - no migration needed

### Technical Challenges

- **InSpec Test Migration**: Converting Chef InSpec compliance tests to native Ansible verification requires rewriting test logic using Ansible modules and assertions
- **Test Framework Replacement**: Migrating from Test Kitchen to Molecule requires restructuring test scenarios and verification approaches
- **Compliance Verification**: Maintaining the same level of security compliance checking without InSpec requires implementing custom Ansible tasks for verification

### Migration Order

1. **InSpec Test Conversion** (Priority 1): Convert Chef InSpec tests in `tests/` directory to Ansible verification tasks
2. **Test Kitchen Replacement** (Priority 2): Replace kitchen.yml with Molecule configuration for playbook testing
3. **Chef Infrastructure Cleanup** (Priority 3): Remove Chef server deployment scripts and dependencies

### Assumptions

- The target environment will continue to use Ubuntu 20.04 LTS as specified in the current Test Kitchen configuration
- Vagrant-based local testing approach will be maintained but migrated to Molecule framework
- Self-signed certificate approach is acceptable for development/testing environments
- The compliance requirements currently verified by InSpec tests (SSH configuration, SSL protocols) remain the same
- No production Chef infrastructure currently depends on the deployment scripts in this repository
- The repository serves as a demonstration/example rather than production infrastructure code