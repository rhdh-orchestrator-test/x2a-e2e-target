# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains demonstration examples for using Chef InSpec alongside Ansible for compliance automation, rather than traditional Chef cookbooks. The migration scope is limited as the repository already contains Ansible playbooks with InSpec tests for validation. The primary migration task involves consolidating the compliance testing approach into native Ansible solutions.

## Module Migration Plan

This repository contains Chef InSpec compliance tests and Ansible playbooks that demonstrate hybrid automation approaches:

### MODULE INVENTORY

**website-https-compliance**:
- Description: Apache HTTPS website deployment with SSL/TLS configuration, self-signed certificate generation, and compliance validation
- Path: chef-and-ansible/
- Technology: Ansible playbooks with Chef InSpec tests
- Key Features: Apache 2.4.41 installation, SSL certificate generation, virtual host configuration, POODLE vulnerability mitigation

**ssh-hardening-compliance**:
- Description: SSH security hardening compliance test ensuring root login is disabled per security benchmarks
- Path: chef-and-ansible/tests/ssh_profile.rb
- Technology: Chef InSpec
- Key Features: STIG compliance (RHEL-08-000227), root login prevention, security audit trail requirements

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `website_https.yml`: Ansible playbook for Apache HTTPS site deployment with SSL configuration
- `poodle_fix.yml`: Ansible playbook for SSL protocol hardening to prevent POODLE attacks
- `deploy-automate.sh`: Chef Automate and Infra Server deployment script for on-premises/cloud VMs
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static test website content

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified, supports both on-premises and cloud deployments

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible native testing modules (assert, uri, stat, service_facts)
- **Test Kitchen**: Replace with Molecule for Ansible testing framework
- **Chef Automate/Server**: Remove dependency as compliance will be handled natively in Ansible

### Security Considerations
- SSL/TLS certificate management: Current implementation uses self-signed certificates via OpenSSL modules - maintain this approach in pure Ansible
- SSH hardening compliance: Migrate InSpec controls to Ansible assert tasks or custom validation modules
- POODLE vulnerability mitigation: Already implemented in Ansible (poodle_fix.yml) - no migration needed
- Credential management: Scripts contain hardcoded passwords for Chef server setup - these should be externalized to Ansible Vault

### Technical Challenges
- **InSpec to Ansible Testing Migration**: Converting Chef InSpec compliance tests to native Ansible validation requires rewriting test logic using Ansible's assert, uri, and service modules
- **Test Kitchen to Molecule**: Migrating the testing framework from Test Kitchen to Molecule for Ansible-native testing workflows
- **Compliance Reporting**: InSpec provides structured compliance reporting - need to implement equivalent reporting in Ansible using callback plugins or custom modules
- **STIG Compliance Mapping**: SSH hardening test references specific STIG controls (RHEL-08-000227) - ensure Ansible implementation maintains compliance mapping

### Migration Order
1. **Website HTTPS Module** (low risk, already in Ansible) - consolidate testing into native Ansible
2. **SSH Hardening Compliance** (moderate complexity) - convert InSpec controls to Ansible validation tasks
3. **Testing Framework Migration** (high complexity) - replace Test Kitchen/InSpec with Molecule/native Ansible testing

### Assumptions
- The repository serves as a demonstration of Chef InSpec + Ansible integration rather than production cookbooks requiring migration
- Target environment will continue using Ubuntu 20.04 LTS as specified in existing configurations
- Self-signed certificates are acceptable for the demonstration use case (production would require proper CA-signed certificates)
- STIG compliance requirements (RHEL-08-000227) must be maintained in the migrated Ansible implementation
- Test Kitchen and Vagrant testing approach can be replaced with Molecule and Docker for faster testing cycles
- Chef Automate/Server deployment scripts are for demonstration purposes and may not require migration if moving to pure Ansible approach