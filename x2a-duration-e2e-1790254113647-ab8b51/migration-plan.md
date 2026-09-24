# MIGRATION FROM CHEF INFRASTRUCTURE TO ANSIBLE

This repository contains Chef infrastructure deployment scripts and Ansible playbook examples demonstrating compliance automation integration. The migration scope is limited as the primary configuration management is already implemented in Ansible playbooks. The main migration effort involves transitioning from Chef Automate/InSpec-based infrastructure deployment to a pure Ansible-based approach.

**Migration Complexity**: Low to Medium
**Estimated Timeline**: 2-4 weeks
**Primary Challenge**: Infrastructure deployment automation and compliance testing integration

## Module Migration Plan

This repository contains Chef infrastructure deployment scripts and Ansible compliance examples that need migration planning:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Ansible playbooks for Apache HTTPS website deployment with SSL configuration, including InSpec compliance verification tests
- Path: chef-and-ansible/
- Technology: Ansible (already migrated) with Chef InSpec testing
- Key Features: Apache 2.4.41 installation, SSL certificate generation, virtual host configuration, POODLE vulnerability mitigation, Test Kitchen integration with InSpec verification

**setup-automate**:
- Description: Bash deployment scripts for Chef Automate and Chef Infra Server infrastructure provisioning
- Path: setup-automate/
- Technology: Bash scripts with Chef server deployment
- Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation, system tuning parameters

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification - requires migration to molecule or native Ansible testing
- `deploy-automate.sh`: Chef Automate deployment script - needs replacement with Ansible infrastructure playbooks
- `deploy-chef-server.sh`: Chef Infra Server deployment script - needs replacement with Ansible infrastructure playbooks
- `website_https_verify.rb`: InSpec compliance tests - requires migration to Ansible compliance modules or integration with ansible-lint/molecule
- `ssh_profile.rb`: SSH security compliance test - needs conversion to Ansible security role verification

### Target Details

- **Operating System**: Ubuntu 20.04 (based on kitchen.yml platform specification and Apache package versions)
- **Virtual Machine Technology**: Vagrant (based on kitchen.yml driver configuration)
- **Cloud Platform**: Not specified (supports on-premises and cloud deployment based on deployment scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate**: Replace with Ansible AWX/Tower or native Ansible automation platform
- **Chef InSpec**: Integrate with ansible-compliance or migrate tests to Ansible native verification
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
- **Chef Infra Server**: Eliminate dependency by using Ansible inventory and configuration management

### Security Considerations

- **SSL Certificate Management**: Current implementation uses self-signed certificates - migration should implement proper certificate authority integration or Let's Encrypt automation
- **SSH Security Configuration**: InSpec SSH compliance tests need conversion to Ansible security role verification with proper hardening standards
- **POODLE Vulnerability Mitigation**: SSL protocol configuration is handled in separate playbook - consolidate into main Apache role for better security management
- **Credential Management**: Deployment scripts contain hardcoded credentials (usernames, passwords, email addresses) - implement Ansible Vault for secrets management

### Technical Challenges

- **Testing Framework Migration**: Transitioning from Test Kitchen + InSpec to Molecule + Ansible native testing requires restructuring test suites and verification methods
- **Infrastructure Deployment**: Chef Automate deployment scripts need complete rewrite as Ansible infrastructure playbooks with proper idempotency and error handling
- **Compliance Integration**: InSpec compliance tests provide detailed security verification - need to maintain equivalent compliance checking in pure Ansible environment
- **Multi-Product Deployment**: Current scripts deploy both Automate and Infra Server - Ansible replacement needs to handle complex multi-service orchestration

### Migration Order

1. **chef-and-ansible playbooks** (already Ansible - focus on testing migration from InSpec to Molecule)
2. **Infrastructure deployment scripts** (replace Chef Automate/Server deployment with Ansible infrastructure roles)
3. **Compliance testing integration** (migrate InSpec tests to Ansible compliance verification)

### Assumptions

- The target environment will continue to use Ubuntu 20.04 as the base operating system
- Vagrant will remain the virtualization platform for development and testing
- The Apache HTTPS website functionality requirements remain unchanged
- SSH security compliance requirements match current InSpec test specifications
- Self-signed certificates are acceptable for development environments, but production may require CA-signed certificates
- The current Chef Automate features (compliance reporting, infrastructure automation) will be replaced with equivalent Ansible-native solutions
- Test Kitchen integration can be fully replaced with Molecule without loss of testing coverage
- The deployment target supports both on-premises and cloud environments as indicated by the current scripts