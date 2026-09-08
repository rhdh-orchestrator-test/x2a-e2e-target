# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible playbooks, rather than traditional Chef cookbooks requiring migration. The primary content consists of Ansible playbooks with Chef InSpec test verification and Chef server deployment scripts. The migration scope is minimal as the infrastructure automation is already implemented in Ansible - the focus should be on replacing Chef InSpec testing with native Ansible testing approaches.

## Module Migration Plan

This repository contains demonstration/example code rather than production infrastructure modules:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Ansible playbook examples demonstrating Apache HTTPS website deployment with SSL configuration and POODLE vulnerability remediation, verified using Chef InSpec tests
- Path: chef-and-ansible/
- Technology: Ansible (with Chef InSpec verification)
- Key Features: Apache 2.4.41 installation, self-signed SSL certificate generation, virtual host configuration, SSL protocol hardening (TLS 1.2 only), Test Kitchen integration for testing

**setup-automate**:
- Description: Bash deployment scripts for Chef Automate and Chef Infra Server installation with user and organization provisioning
- Path: setup-automate/
- Technology: Bash scripts (Chef server deployment)
- Key Features: Chef Automate CLI deployment, Chef Infra Server setup, user/organization creation, system tuning (vm.max_map_count, vm.dirty_expire_centisecs)

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `website_https.yml`: Ansible playbook for Apache HTTPS site deployment with SSL certificate management
- `poodle_fix.yml`: Ansible playbook for SSL protocol hardening (disabling SSLv3, enabling TLS 1.2)
- `website_https_verify.rb`: Chef InSpec test suite verifying HTTPS functionality and SSL protocol configuration
- `ssh_profile.rb`: Chef InSpec compliance test for SSH root login security (STIG control)
- `deploy-automate.sh`: Chef Automate and Infra Server deployment automation
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured as Test Kitchen driver)
- **Cloud Platform**: Not specified (examples designed for on-premises or cloud VM deployment)

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with ansible-lint, molecule testing framework, or native Ansible assert modules
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and verification
- **Chef Automate/Server**: Evaluate need for centralized configuration management - consider Ansible Tower/AWX or Ansible Automation Platform

### Security Considerations
- SSL/TLS certificate management: The playbooks use self-signed certificates for demonstration - production migration should integrate with proper certificate authorities or certificate management systems
- SSH hardening verification: The InSpec SSH compliance test (STIG control RHEL-08-000227) should be converted to Ansible security role or custom verification tasks
- Credential management: The Chef server deployment scripts contain hardcoded credentials that should be externalized to Ansible Vault or secure credential management systems

### Technical Challenges
- **Testing Framework Migration**: Converting Chef InSpec tests to equivalent Ansible testing approaches requires rewriting test logic in Ansible assert modules or integrating alternative testing frameworks
- **Compliance Verification**: The SSH security compliance test follows STIG standards - ensure equivalent security validation in pure Ansible approach
- **Chef Infrastructure Dependencies**: If the organization relies on Chef Automate for reporting and compliance, evaluate Ansible Automation Platform as replacement or maintain hybrid approach

### Migration Order
1. **chef-and-ansible playbooks** (low risk - already Ansible, only testing needs conversion)
2. **InSpec test conversion** (moderate complexity - requires testing framework decisions)
3. **Chef server deployment scripts** (evaluate necessity - may be deprecated if moving to pure Ansible)

### Assumptions
- This repository serves as example/demonstration code rather than production infrastructure requiring migration
- The organization is evaluating replacing Chef InSpec testing with native Ansible testing approaches
- Chef Automate/Server infrastructure may be deprecated in favor of Ansible-native solutions
- The Apache HTTPS configuration represents a pattern used in production environments that needs testing framework migration
- SSL certificate management approach (self-signed) is acceptable for demonstration but would need enhancement for production use
- Ubuntu 20.04 target platform is representative of production environment requirements
- Test Kitchen + Vagrant testing approach needs replacement with Molecule or similar Ansible-native testing framework