# MIGRATION FROM MIXED ANSIBLE/CHEF INSPEC TO ANSIBLE

This repository is a demonstration/example repository that showcases integration between Ansible and Chef InSpec for compliance automation. It does not contain traditional Chef cookbooks requiring migration, but rather existing Ansible playbooks with Chef InSpec testing. The migration scope is minimal as the primary automation is already in Ansible format.

## Module Migration Plan

This repository contains demonstration Ansible playbooks and Chef InSpec compliance tests that require assessment for production use:

### MODULE INVENTORY

**apache-https-website**:
- Description: Apache web server configuration with SSL/TLS setup, self-signed certificate generation, and virtual host deployment for a simple "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: SSL certificate generation via OpenSSL modules, Apache virtual host configuration, package management for Ubuntu 20.04

**ssl-security-hardening**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols (POODLE vulnerability fix) and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, vulnerability remediation, service restart handling

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Static HTML content for web server testing
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script for lab environments
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL configuration
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec compliance profile for SSH security hardening verification

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml and playbook package versions)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen for local development/testing)
- **Cloud Platform**: Not specified (deployment scripts suggest on-premises or generic cloud VM deployment)

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible compliance testing using ansible-lint, molecule, or native Ansible testing modules
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and verification
- **Chef Automate/Server**: Evaluate need for centralized compliance reporting - consider Ansible Tower/AWX or third-party compliance tools

### Security Considerations
- **Hardcoded credentials**: The deployment scripts contain hardcoded usernames, passwords, and email addresses that must be externalized to Ansible Vault or environment variables
- **SSL certificate management**: Current implementation uses self-signed certificates - production deployment should integrate with proper CA or Let's Encrypt
- **SSH security**: InSpec tests verify SSH hardening but corresponding Ansible configuration is missing - need SSH hardening playbook
- **Compliance verification**: Chef InSpec tests provide security compliance validation - need equivalent Ansible-native testing approach

### Technical Challenges
- **Testing framework migration**: Converting Chef InSpec tests to Ansible-native testing requires rewriting compliance verification logic
- **Compliance reporting**: Loss of Chef Automate's compliance dashboard requires alternative reporting solution
- **Test Kitchen replacement**: Molecule learning curve for teams familiar with Test Kitchen workflow
- **Certificate automation**: Production-ready certificate management beyond self-signed certificates

### Migration Order
1. **SSL hardening playbook** (low risk, security-focused, already in Ansible format)
2. **Apache website playbook** (moderate complexity, requires certificate management strategy)
3. **Compliance testing framework** (high complexity, requires tool evaluation and team training)
4. **Infrastructure deployment automation** (lowest priority, affects lab/development environments only)

### Assumptions
- The repository serves as a demonstration/training resource rather than production infrastructure code
- Teams are already familiar with Ansible syntax and modules based on existing playbook quality
- Chef InSpec knowledge exists in the team for compliance test conversion
- Production deployments will require proper certificate management beyond self-signed certificates
- The Test Kitchen + InSpec workflow is currently used for validation and needs Ansible-native replacement
- Deployment scripts are used for lab/development environments and may not require migration to Ansible
- Ubuntu package versions in playbooks may need updates for current production use
- SSH hardening configuration is missing despite having InSpec tests for SSH security verification