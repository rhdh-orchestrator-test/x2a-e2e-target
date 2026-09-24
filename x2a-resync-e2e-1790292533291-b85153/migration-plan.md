# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible for compliance automation. The repository is already primarily Ansible-based with InSpec used for testing and compliance verification. This represents a hybrid approach rather than a traditional Chef-to-Ansible migration scenario.

## Module Migration Plan

This repository contains demonstration examples and deployment scripts that showcase Chef InSpec integration with Ansible:

### MODULE INVENTORY

**website-https-demo**:
- Description: Apache web server with HTTPS/SSL configuration, self-signed certificate generation, and virtual host setup for demonstration purposes
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, directory structure creation

**poodle-vulnerability-fix**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible
- Key Features: Apache SSL configuration hardening, protocol restriction, POODLE vulnerability mitigation

**chef-infrastructure-deployment**:
- Description: Bash deployment scripts for Chef Automate and Chef Infra Server installation and initial configuration
- Path: setup-automate/
- Technology: Bash scripts
- Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation, system tuning

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality, SSL protocol verification, and port accessibility
- `tests/ssh_profile.rb`: InSpec security control for SSH root login restrictions (STIG compliance)
- `index.html`: Static HTML test content for web server validation
- `README.md`: Documentation explaining Chef InSpec and Ansible integration approach

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Already integrated for compliance testing - no migration needed, continue using for security validation
- **Test Kitchen**: Currently configured for testing infrastructure - can be retained or replaced with molecule for Ansible-native testing
- **Apache 2.4.41**: Specific version pinned in playbook - verify availability in target repositories
- **OpenSSL Python bindings**: Required for certificate generation - ensure python3-openssl package availability

### Security Considerations
- **Self-signed certificates**: Current implementation uses self-signed certificates for demonstration - production deployment should integrate with proper CA or Let's Encrypt
- **Hardcoded credentials**: Deployment scripts contain plaintext passwords and usernames - should be externalized to Ansible Vault or environment variables
- **SSL/TLS configuration**: POODLE fix demonstrates security hardening - ensure all SSL configurations follow current security best practices
- **SSH security**: InSpec tests verify SSH root login restrictions - maintain these compliance checks in production

### Technical Challenges
- **Hybrid testing approach**: Repository demonstrates InSpec integration with Ansible - decision needed on whether to maintain this approach or migrate to native Ansible testing
- **Chef infrastructure dependencies**: Deployment scripts install Chef Automate/Server - if migrating away from Chef ecosystem, these scripts become obsolete
- **Test Kitchen vs Molecule**: Current Test Kitchen setup may need migration to Molecule for pure Ansible workflow
- **Compliance framework**: InSpec provides STIG-based compliance testing - alternative compliance frameworks may be needed if removing Chef dependencies

### Migration Order
1. **Ansible playbooks** (already complete - no migration needed)
2. **InSpec compliance tests** (evaluate retention vs migration to Ansible-native compliance tools)
3. **Chef infrastructure scripts** (replace with Ansible-based infrastructure deployment if removing Chef dependencies)

### Assumptions
- The repository serves as demonstration/example code rather than production infrastructure requiring migration
- Current Ansible playbooks are already production-ready and follow best practices
- InSpec integration provides value for compliance automation and should be retained unless organizational policy requires pure Ansible toolchain
- Chef Automate/Server deployment scripts are only needed if maintaining Chef infrastructure for other purposes
- Test Kitchen configuration suggests development/testing environment rather than production deployment
- Ubuntu 20.04 target platform is acceptable for production use (may need updates to newer LTS versions)
- Self-signed certificate approach is acceptable for demonstration but will need proper certificate management for production
- Hardcoded credentials in deployment scripts are acceptable for demo purposes but must be secured for any real deployment