# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains demonstration examples for using Chef InSpec alongside Ansible for compliance automation, rather than traditional Chef cookbooks. The migration scope is limited as the repository already contains Ansible playbooks with InSpec verification tests. The primary migration task involves consolidating the compliance testing approach into native Ansible solutions.

## Module Migration Plan

This repository contains Chef InSpec compliance tests and Ansible playbooks that demonstrate integration patterns:

### MODULE INVENTORY

**website-https-compliance**:
- Description: Apache HTTPS website deployment with SSL/TLS configuration, self-signed certificate generation, and compliance verification
- Path: chef-and-ansible/
- Technology: Ansible playbook with Chef InSpec verification
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, POODLE vulnerability mitigation

**ssh-security-compliance**:
- Description: SSH security hardening compliance test ensuring root login is disabled per security benchmarks
- Path: chef-and-ansible/tests/ssh_profile.rb
- Technology: Chef InSpec
- Key Features: STIG compliance (RHEL-08-000227), root login prevention, security control SRG-OS-000112

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `website_https.yml`: Ansible playbook for Apache HTTPS setup with SSL certificate management
- `poodle_fix.yml`: Ansible playbook for SSL protocol hardening to prevent POODLE attacks
- `deploy-automate.sh`: Chef Automate and Infra Server deployment script for on-premises/cloud VMs
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified, supports both on-premises and cloud deployments

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with native Ansible compliance modules (ansible.posix.mount, community.general.system_info)
- **Test Kitchen**: Migrate to Ansible Molecule for testing framework
- **Chef Automate/Server**: Replace with Ansible AWX/Tower for centralized automation management

### Security Considerations
- SSL/TLS certificate management: Current implementation uses self-signed certificates via OpenSSL Ansible modules - production migration should integrate with proper CA or Let's Encrypt
- SSH hardening compliance: InSpec test verifies PermitRootLogin=no - migrate to ansible.posix.sshd_config module with validation
- POODLE vulnerability mitigation: SSL protocol configuration hardening already implemented in Ansible
- Credential management: Deployment scripts contain hardcoded passwords and usernames that need vault encryption

### Technical Challenges
- **InSpec to Ansible Testing**: Converting Chef InSpec compliance tests to native Ansible assert modules or Molecule verifiers
- **Test Kitchen Migration**: Replacing Test Kitchen workflow with Ansible Molecule for integrated testing
- **Compliance Framework**: Maintaining STIG/CIS compliance verification without InSpec dependency
- **Certificate Management**: Transitioning from self-signed certificates to production-ready certificate automation

### Migration Order
1. **SSL/TLS Playbook Enhancement** (low risk, already Ansible-native)
2. **SSH Compliance Integration** (moderate complexity, convert InSpec tests to Ansible tasks)
3. **Testing Framework Migration** (high complexity, Test Kitchen to Molecule conversion)

### Assumptions
- The repository serves as a demonstration/example rather than production infrastructure code
- Current Ansible playbooks are functional and represent the desired end state for most configurations
- InSpec tests represent compliance requirements that must be maintained in the migrated solution
- The Chef Automate/Server deployment scripts are for development/testing environments only
- SSL certificate requirements will evolve from self-signed to proper CA-issued certificates in production
- Ubuntu 20.04 target platform will be maintained or upgraded to a supported LTS version
- Test Kitchen usage indicates a preference for local development testing that should be preserved in Molecule