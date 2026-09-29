# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains Chef InSpec compliance tests and Ansible playbooks demonstrating hybrid automation approaches. The migration involves consolidating InSpec testing capabilities into native Ansible testing frameworks while preserving compliance validation functionality. The scope is limited with low complexity, estimated timeline of 1-2 weeks for a small team.

## Module Migration Plan

This repository contains demonstration content that combines Chef InSpec testing with Ansible automation:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Ansible playbooks for Apache HTTPS configuration with SSL/TLS security hardening and Chef InSpec compliance verification
- Path: chef-and-ansible/
- Technology: Ansible + Chef InSpec
- Key Features: Apache 2.4.41 installation, self-signed SSL certificate generation, POODLE vulnerability mitigation, HTTPS virtual host configuration, compliance testing for port 443 and SSL protocols

**setup-automate**:
- Description: Bash deployment scripts for Chef Automate and Chef Infra Server infrastructure provisioning
- Path: setup-automate/
- Technology: Bash scripts
- Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation, system tuning (vm.max_map_count, vm.dirty_expire_centisecs)

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `website_https.yml`: Ansible playbook for Apache HTTPS setup with SSL certificate management
- `poodle_fix.yml`: Ansible playbook for SSL protocol hardening (disables SSLv3, enables TLSv1.2)
- `website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `ssh_profile.rb`: InSpec security control for SSH root login restrictions (STIG compliance)
- `deploy-automate.sh`: Chef Automate deployment automation script
- `deploy-chef-server.sh`: Chef Infra Server deployment automation script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified (designed for on-premises or cloud VM deployment)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing modules (uri, assert, service_facts) and external testing frameworks like Molecule or Testinfra
- **Test Kitchen**: Migrate to Ansible Molecule for testing and validation workflows
- **Chef Automate/Server**: Replace with Ansible Tower/AWX or native Ansible automation for infrastructure management

### Security Considerations

- **SSL/TLS Configuration**: Current implementation uses self-signed certificates and hardcoded SSL protocols - migrate to Ansible certificate management with proper CA integration
- **SSH Hardening**: InSpec SSH compliance controls need conversion to Ansible security roles or hardening playbooks
- **Credential Management**: Deployment scripts contain hardcoded passwords and usernames - implement Ansible Vault for secrets management
- **STIG Compliance**: SSH root login restrictions and other security controls require native Ansible security automation

### Technical Challenges

- **InSpec Test Migration**: Converting Ruby-based InSpec controls to Ansible testing requires rewriting test logic in YAML/Jinja2 format
- **Compliance Framework**: Loss of Chef InSpec's extensive compliance library necessitates building equivalent Ansible security roles
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule requires restructuring test scenarios and verification methods
- **Infrastructure Deployment**: Chef Automate/Server deployment scripts need conversion to Ansible infrastructure-as-code playbooks

### Migration Order

1. **chef-and-ansible** (low risk, high value) - Convert existing Ansible playbooks to pure Ansible with native testing
2. **setup-automate** (moderate complexity) - Replace deployment scripts with Ansible infrastructure playbooks
3. **Compliance Testing** (high complexity) - Implement comprehensive Ansible-based security and compliance automation

### Assumptions

- The repository serves as a demonstration/proof-of-concept rather than production infrastructure code
- Target environment will accept native Ansible testing in place of Chef InSpec compliance validation
- Team has access to Ansible security roles or willingness to develop custom compliance automation
- Infrastructure deployment can be migrated from bash scripts to Ansible infrastructure playbooks
- Test Kitchen workflows can be replaced with Ansible Molecule or similar testing frameworks
- SSL certificate management will be enhanced beyond self-signed certificates in production migration
- Hardcoded credentials in deployment scripts will be properly secured using Ansible Vault
- Ubuntu 20.04 target platform is acceptable for the migrated Ansible automation
- Vagrant-based testing environment is suitable for continued development and validation