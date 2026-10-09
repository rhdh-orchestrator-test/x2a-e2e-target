# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains Chef InSpec compliance tests and Ansible playbooks demonstrating hybrid automation approaches. The migration involves consolidating InSpec testing capabilities into native Ansible testing modules and standardizing on Ansible for both configuration management and compliance verification. The scope is limited with low complexity, estimated timeline of 1-2 weeks for a single engineer.

## Module Migration Plan

This repository contains demonstration content that combines Chef InSpec testing with Ansible automation:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Ansible playbooks for Apache HTTPS configuration with SSL/TLS security hardening and Chef InSpec compliance verification
- Path: chef-and-ansible
- Technology: Ansible + Chef InSpec
- Key Features: Apache 2.4.41 installation, self-signed SSL certificate generation, virtual host configuration, POODLE vulnerability mitigation, Test Kitchen integration

**setup-automate**:
- Description: Bash deployment scripts for Chef Automate and Chef Infra Server infrastructure provisioning
- Path: setup-automate  
- Technology: Bash scripts
- Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation, system tuning parameters

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible provisioning with InSpec verification - needs migration to molecule or native Ansible testing
- `website_https.yml`: Ansible playbook for Apache HTTPS setup - already in target format, requires testing strategy migration
- `poodle_fix.yml`: Ansible playbook for SSL protocol hardening - already in target format
- `website_https_verify.rb`: InSpec compliance tests for HTTPS functionality - needs conversion to Ansible testing modules
- `ssh_profile.rb`: InSpec SSH security compliance profile - needs conversion to Ansible testing modules
- `deploy-automate.sh`: Chef infrastructure deployment script - needs conversion to Ansible playbook
- `deploy-chef-server.sh`: Chef server deployment script - needs conversion to Ansible playbook

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with ansible-lint, molecule testing framework, and native Ansible assert modules
- **Test Kitchen**: Replace with Molecule for infrastructure testing and validation
- **Chef Automate/Server**: Replace with Ansible AWX/Tower or native Ansible automation platform

### Security Considerations
- SSL/TLS certificate management: Current self-signed certificate generation needs production-ready certificate authority integration
- SSH hardening compliance: InSpec SSH security controls need conversion to Ansible security role with built-in compliance verification
- Apache security configuration: POODLE vulnerability mitigation and SSL protocol restrictions require ongoing compliance monitoring
- Credential management: Deployment scripts contain hardcoded passwords that need migration to Ansible Vault

### Technical Challenges
- **InSpec to Ansible Testing Migration**: Converting Ruby-based InSpec controls to Ansible native testing requires rewriting test logic using assert, uri, and command modules
- **Test Kitchen to Molecule**: Kitchen.yml configuration needs complete restructuring for Molecule testing framework with different syntax and workflow
- **Compliance Automation**: Maintaining continuous compliance verification without InSpec requires implementing Ansible-native compliance checking patterns

### Migration Order
1. **chef-and-ansible playbooks** (already Ansible - focus on testing migration)
2. **setup-automate deployment scripts** (convert Bash to Ansible playbooks)
3. **InSpec compliance tests** (convert to Ansible testing modules and molecule scenarios)

### Assumptions
- The repository serves as demonstration/training content rather than production infrastructure code
- Target environment will use Ansible AWX/Tower instead of Chef Automate for automation platform
- SSL certificate management will be enhanced beyond self-signed certificates for production use
- Test Kitchen workflow will be completely replaced by Molecule testing framework
- InSpec compliance profiles will be converted to Ansible security roles with integrated testing
- Hardcoded credentials in deployment scripts are acceptable for demo purposes but will need Ansible Vault in production