# MIGRATION FROM CHEF INSPEC/ANSIBLE HYBRID TO ANSIBLE

This repository contains Chef InSpec compliance testing examples integrated with Ansible playbooks, plus Chef server deployment automation. The migration scope is limited as most content is already Ansible-based, with the primary task being to replace Chef InSpec testing with native Ansible testing approaches. Timeline estimate: 1-2 weeks for a small team.

## Module Migration Plan

This repository contains hybrid Chef/Ansible examples and deployment scripts that need individual migration planning:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Ansible playbooks for Apache HTTPS website deployment with Chef InSpec compliance verification
- Path: chef-and-ansible/
- Technology: Ansible + Chef InSpec
- Key Features: SSL certificate generation, Apache virtual host configuration, POODLE vulnerability remediation, compliance testing via InSpec

**setup-automate**:
- Description: Bash scripts for automated Chef Automate and Chef Infra Server deployment
- Path: setup-automate/
- Technology: Bash + Chef CLI
- Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration using Ansible provisioner with InSpec verifier - needs migration to molecule or native Ansible testing
- `website_https.yml`: Complete Ansible playbook for Apache HTTPS setup - already migrated, no changes needed
- `poodle_fix.yml`: Ansible playbook for SSL security hardening - already migrated, no changes needed
- `website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality - needs replacement with Ansible testing
- `ssh_profile.rb`: Chef InSpec SSH security compliance tests - needs replacement with Ansible testing
- `deploy-automate.sh`: Chef server deployment script - needs replacement with Ansible playbook
- `deploy-chef-server.sh`: Chef Infra server deployment script - needs replacement with Ansible playbook

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml), with RHEL compatibility considerations for SSH hardening tests
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with ansible-lint, molecule testing framework, or native Ansible assert modules
- **Test Kitchen**: Replace with Molecule for infrastructure testing
- **Chef CLI tools**: Replace chef-server-ctl commands with Ansible modules for Chef server management or migrate to alternative configuration management

### Security Considerations
- SSL/TLS certificate management: Current implementation uses self-signed certificates via OpenSSL Ansible modules - already properly migrated
- SSH hardening compliance: InSpec tests verify PermitRootLogin disabled and SSL protocol restrictions - needs conversion to Ansible assert tasks
- Apache security configuration: POODLE vulnerability fix already implemented in Ansible - no migration needed
- Credential management: Hardcoded passwords in deployment scripts need migration to Ansible Vault

### Technical Challenges
- **InSpec to Ansible Testing Migration**: Converting Ruby-based InSpec controls to Ansible assert tasks or molecule tests requires rewriting test logic
- **Chef Server Deployment**: Bash scripts use chef-server-ctl commands that need replacement with Ansible modules or API calls
- **Test Kitchen Integration**: Current Vagrant + InSpec workflow needs migration to Molecule + pytest or native Ansible testing
- **Compliance Framework**: InSpec provides STIG/CIS compliance mappings that need equivalent Ansible security role implementation

### Migration Order
1. **chef-and-ansible playbooks** (already migrated - validation only needed)
2. **InSpec test conversion** (moderate complexity - rewrite Ruby tests as Ansible tasks)
3. **Chef server deployment scripts** (high complexity - replace CLI tools with Ansible automation)

### Assumptions
- The primary goal is maintaining compliance testing capabilities while removing Chef InSpec dependency
- Existing Ansible playbooks (website_https.yml, poodle_fix.yml) are considered migration targets rather than sources
- Chef server deployment automation will be replaced entirely with Ansible-based solutions
- Test Kitchen workflow will be replaced with Molecule for infrastructure testing
- Current SSL certificate generation approach using Ansible OpenSSL modules is acceptable for the target environment
- SSH hardening requirements follow RHEL 8 STIG guidelines as indicated in the InSpec control metadata