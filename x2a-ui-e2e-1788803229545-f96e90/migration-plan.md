# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains demonstration examples of Chef InSpec integration with Ansible playbooks rather than traditional Chef cookbooks requiring migration. The primary content consists of Ansible playbooks with Chef InSpec test verification and Chef server deployment scripts. Migration complexity is minimal as the core automation is already in Ansible format.

## Module Migration Plan

This repository contains example configurations and deployment scripts that demonstrate Chef InSpec testing alongside Ansible automation:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Ansible playbook demonstrating HTTPS website deployment with Apache SSL configuration, including SSL certificate generation and virtual host setup
- Path: chef-and-ansible/
- Technology: Ansible (with Chef InSpec testing)
- Key Features: Apache 2.4 installation, self-signed SSL certificate generation, virtual host configuration, POODLE vulnerability mitigation

**setup-automate**:
- Description: Bash deployment scripts for Chef Automate and Chef Infra Server installation with user and organization provisioning
- Path: setup-automate/
- Technology: Bash scripts (Chef server deployment)
- Key Features: Chef Automate deployment, Chef Infra Server setup, user/organization creation, system tuning parameters

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `website_https.yml`: Main Ansible playbook for Apache HTTPS site deployment
- `poodle_fix.yml`: Ansible playbook for SSL protocol hardening (disables SSLv3, enables TLS 1.2)
- `website_https_verify.rb`: Chef InSpec test suite verifying HTTPS functionality and SSL protocol configuration
- `ssh_profile.rb`: Chef InSpec compliance test for SSH root login security controls
- `deploy-automate.sh`: Chef Automate and Infra Server deployment automation
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured as Test Kitchen driver)
- **Cloud Platform**: Not specified (designed for on-premises or cloud VM deployment)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible molecule testing framework or native Ansible assert modules
- **Test Kitchen**: Migrate to Ansible molecule for testing and verification workflows
- **Chef Automate/Server**: Evaluate need for centralized configuration management - consider Ansible Tower/AWX or Ansible Automation Platform

### Security Considerations

- **SSL/TLS Configuration**: Current playbooks generate self-signed certificates - production migration should integrate with proper CA or certificate management
- **SSH Hardening**: InSpec tests verify SSH root login disabled - ensure equivalent Ansible security hardening tasks
- **Credential Management**: Deployment scripts contain hardcoded passwords - migrate to Ansible Vault or external secret management
- **SSL Protocol Security**: POODLE fix playbook demonstrates security patching - ensure similar security controls in migrated automation

### Technical Challenges

- **Testing Framework Migration**: Converting Chef InSpec tests to Ansible molecule or native testing requires rewriting test specifications
- **Compliance Verification**: InSpec compliance controls need translation to Ansible security role equivalents or custom verification tasks
- **Chef Server Dependencies**: If organization relies on Chef server infrastructure, plan migration to Ansible control nodes and inventory management

### Migration Order

1. **chef-and-ansible playbooks** (already Ansible - minimal migration needed, focus on testing framework)
2. **setup-automate scripts** (evaluate if Chef infrastructure still needed post-migration)
3. **InSpec test suites** (convert to Ansible molecule or assert-based testing)

### Assumptions

- Repository serves as demonstration/example code rather than production infrastructure requiring migration
- Current Ansible playbooks are functional and follow acceptable practices for the demonstration purpose
- Chef InSpec testing framework provides value that should be preserved in equivalent Ansible testing approach
- Chef server deployment scripts may become obsolete if migrating away from Chef ecosystem entirely
- SSL certificate management approach (self-signed) is acceptable for demonstration but would need enhancement for production use
- Ubuntu 20.04 target platform assumption based on Test Kitchen configuration may need validation for actual deployment targets
- Hardcoded credentials in deployment scripts are acceptable for demo purposes but require proper secret management for production migration