# MIGRATION FROM MIXED ANSIBLE/CHEF EXAMPLES TO STANDARDIZED ANSIBLE

This repository contains Ansible playbooks with Chef InSpec testing integration that demonstrates compliance automation patterns. The migration involves standardizing the existing Ansible content, improving the Chef InSpec integration, and establishing best practices for infrastructure-as-code with compliance testing.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need standardization and enhancement:

### MODULE INVENTORY

**website-https**:
- Description: Apache web server deployment with SSL/TLS configuration, self-signed certificate generation, and virtual host setup
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

**poodle-fix**:
- Description: SSL security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible
- Key Features: Apache SSL protocol configuration, POODLE vulnerability mitigation, service restart handlers

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `index.html`: Static HTML test content for web server validation
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality, SSL protocol validation, and service availability
- `tests/ssh_profile.rb`: Chef InSpec security compliance test for SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for compliance infrastructure
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox provider (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address

- **apache2=2.4.41-4ubuntu3.10**: Pinned Apache version needs evaluation for security updates and compatibility
- **python3-openssl**: Required for Ansible OpenSSL certificate management modules
- **Chef InSpec**: External testing framework dependency for compliance validation
- **Test Kitchen**: Development testing framework requiring Ruby environment
- **Vagrant**: Local virtualization dependency for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: Current implementation uses self-signed certificates suitable for testing but requires CA-signed certificates for production
- **Hardcoded Credentials**: Chef Automate deployment scripts contain plaintext passwords and need vault integration:
  - Username: 'jtonello' 
  - Password: 'password'
  - Email: 'jtonello@chef.lab'
  - Organization credentials in deployment scripts
- **SSH Security**: InSpec tests validate SSH root login restrictions but playbooks don't implement SSH hardening
- **Certificate Management**: Self-signed certificate generation needs integration with proper PKI infrastructure
- **Service Handlers**: Apache and SSH service restart handlers present potential security risks during deployment

### Technical Challenges

- **Mixed Technology Stack**: Integration between Ansible automation and Chef InSpec compliance testing requires careful coordination
- **Testing Infrastructure**: Test Kitchen configuration assumes Vagrant/VirtualBox environment limiting CI/CD integration
- **Version Pinning**: Apache package version pinning may cause compatibility issues with security updates
- **Handler Dependencies**: Service restart handlers have unclear dependencies that could cause deployment failures
- **SSL Protocol Configuration**: Regex-based SSL configuration replacement is brittle and error-prone

### Migration Order

1. **website-https** (moderate complexity, foundational infrastructure)
2. **poodle-fix** (low complexity, security enhancement dependent on website-https)
3. **InSpec Integration** (high complexity, requires both playbooks to be functional)

### Assumptions

- The repository serves as a demonstration/example rather than production infrastructure code
- Ubuntu 20.04 is the target platform though no explicit OS detection or multi-platform support exists
- Self-signed certificates are acceptable for the demonstration use case
- Local development environment using Vagrant is the primary testing approach
- Chef InSpec knowledge exists within the team for compliance testing
- The hardcoded credentials in deployment scripts are for demonstration purposes only
- Apache 2.4.41 version pinning is intentional for reproducible testing rather than security requirements
- SSH service restart in handlers is intentional though the relationship to Apache configuration is unclear
- Test Kitchen and Ruby development environment are available for testing workflows
- The integration between Ansible and Chef InSpec represents a desired compliance automation pattern rather than a temporary solution