# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains demonstration examples for using Chef InSpec alongside Ansible for compliance automation, rather than traditional Chef cookbooks. The migration scope is limited as the repository already contains Ansible playbooks with InSpec tests for validation. The primary migration task involves consolidating the compliance testing approach into native Ansible solutions.

## Module Migration Plan

This repository contains Chef InSpec compliance tests and Ansible playbooks that demonstrate integration patterns:

### MODULE INVENTORY

**website-https-compliance**:
- Description: Apache HTTPS website deployment with SSL/TLS configuration, self-signed certificate generation, and security compliance validation
- Path: chef-and-ansible/
- Technology: Ansible playbooks with Chef InSpec tests
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, POODLE vulnerability mitigation

**ssh-security-compliance**:
- Description: SSH security hardening compliance test ensuring root login is disabled per security benchmarks
- Path: chef-and-ansible/tests/ssh_profile.rb
- Technology: Chef InSpec
- Key Features: STIG compliance (RHEL-08-000227), root login prevention, audit trail requirements

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `website_https.yml`: Ansible playbook for Apache HTTPS setup with SSL configuration
- `poodle_fix.yml`: Ansible playbook for SSL protocol hardening (disables SSLv3, enables TLS 1.2)
- `index.html`: Static test content for website validation
- `deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured as Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with ansible-lint, molecule testing, or native Ansible assert modules
- **Test Kitchen**: Replace with Molecule for Ansible testing framework
- **Chef Automate/Server**: Remove dependency as compliance will be handled natively in Ansible

### Security Considerations

- **SSL/TLS Certificate Management**: Current implementation uses self-signed certificates generated via OpenSSL Ansible modules - this approach can be retained or enhanced with Let's Encrypt integration
- **SSH Hardening**: InSpec test validates SSH root login prevention - migrate to Ansible assert tasks or use ansible-hardening role
- **POODLE Vulnerability Mitigation**: SSL protocol configuration is already implemented in Ansible - no migration needed
- **Compliance Validation**: Replace InSpec compliance tests with:
  - Ansible assert modules for runtime validation
  - ansible-lint for static analysis
  - Custom Ansible modules for STIG compliance checking

### Technical Challenges

- **Testing Framework Migration**: Replacing Test Kitchen + InSpec with Molecule + pytest requires restructuring test scenarios and validation logic
- **Compliance Reporting**: InSpec provides structured compliance reporting - need to implement equivalent reporting mechanism using Ansible facts and custom modules
- **Continuous Compliance**: Current approach allows ongoing compliance validation - ensure Ansible solution maintains this capability through scheduled playbook runs or AWX/Tower integration

### Migration Order

1. **SSL/TLS Configuration** (already in Ansible - validate and enhance)
2. **SSH Security Hardening** (convert InSpec tests to Ansible assert tasks)
3. **Testing Framework** (implement Molecule testing to replace Test Kitchen)
4. **Compliance Reporting** (develop Ansible-native compliance validation and reporting)

### Assumptions

- The repository serves as a demonstration/example rather than production infrastructure code
- Target environment will continue using Ubuntu/Debian-based systems (apt package manager usage)
- Self-signed certificates are acceptable for the demonstration use case
- Test Kitchen and Chef InSpec dependencies can be completely removed in favor of Ansible-native testing
- The Chef Automate/Server deployment scripts are for lab setup only and not part of the migration scope
- Compliance requirements (STIG controls) remain the same but validation method will change from InSpec to Ansible
- Current SSL/TLS security configurations meet organizational requirements and should be preserved
- The migration timeline assumes this is a low-priority demonstration repository rather than critical production infrastructure