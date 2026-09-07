# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible for compliance automation. The repository is already primarily Ansible-based with InSpec used for testing and compliance verification. This represents a hybrid approach rather than a traditional Chef-to-Ansible migration scenario.

## Module Migration Plan

This repository contains demonstration examples and deployment scripts that showcase compliance automation patterns:

### MODULE INVENTORY

**website-https-demo**:
- Description: Apache HTTPS website deployment with SSL certificate generation, virtual host configuration, and security hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible
- Key Features: Self-signed SSL certificates via OpenSSL modules, Apache virtual host configuration, security compliance verification

**poodle-vulnerability-fix**:
- Description: SSL/TLS security hardening to address POODLE vulnerability by disabling SSLv3 and enforcing TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible
- Key Features: Apache SSL protocol configuration, security compliance remediation

**chef-infrastructure-deployment**:
- Description: Automated deployment scripts for Chef Automate and Chef Infra Server infrastructure
- Path: setup-automate/
- Technology: Bash scripts
- Key Features: Chef Automate installation, Chef Infra Server setup, user and organization provisioning

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL/TLS security
- `tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance (STIG controls)
- `index.html`: Static HTML test content for web server verification
- `deploy-automate.sh`: Chef Automate and Infra Server deployment automation
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

**No traditional migration required** - this repository demonstrates a hybrid approach where:
- **Ansible**: Already handles configuration management and deployment tasks
- **Chef InSpec**: Provides compliance testing and security verification
- **Test Kitchen**: Orchestrates testing workflow with Ansible provisioner and InSpec verifier

### Security Considerations

- **SSL/TLS Management**: Self-signed certificate generation using Ansible OpenSSL modules
  - Current approach uses openssl_privatekey, openssl_csr, and openssl_certificate modules
  - Production environments should integrate with proper CA or certificate management solutions
- **SSH Security Compliance**: InSpec profiles verify SSH root login restrictions per STIG requirements
  - Control SRG-OS-000112 ensures PermitRootLogin is disabled
  - Compliance verification automated through InSpec testing
- **Apache Security Hardening**: POODLE vulnerability mitigation through SSL protocol restrictions
  - Disables SSLv3 protocol to prevent POODLE attacks
  - Enforces TLS 1.2 minimum protocol version

### Technical Challenges

- **InSpec Integration Complexity**: The current hybrid approach requires maintaining both Ansible and InSpec expertise
  - **Mitigation**: Consider migrating InSpec tests to native Ansible testing modules or molecule for simplified toolchain
- **Certificate Management**: Self-signed certificates are suitable for testing but not production
  - **Mitigation**: Integrate with Let's Encrypt via certbot or enterprise CA solutions
- **Deployment Script Dependencies**: Bash scripts for Chef infrastructure deployment create external dependencies
  - **Mitigation**: Convert deployment scripts to Ansible playbooks for consistency

### Migration Order

This repository doesn't require traditional migration but could benefit from consolidation:

1. **Maintain Current Hybrid Approach** (if InSpec compliance testing is required)
   - Keep existing Ansible playbooks
   - Maintain InSpec profiles for compliance verification
   - Continue using Test Kitchen for integration testing

2. **Consolidate to Pure Ansible** (if simplified toolchain is preferred)
   - Convert InSpec tests to Ansible assert modules or molecule tests
   - Replace Test Kitchen with molecule for testing workflow
   - Maintain compliance verification through Ansible native testing

3. **Infrastructure Deployment Modernization**
   - Convert Bash deployment scripts to Ansible playbooks
   - Implement idempotent Chef infrastructure provisioning
   - Add proper secret management for credentials

### Assumptions

- The repository serves as demonstration/example code rather than production infrastructure
- InSpec compliance testing requirements may necessitate maintaining the hybrid approach
- Test Kitchen integration with Vagrant assumes local development environment usage
- Chef infrastructure deployment scripts target single-node installations
- SSL certificate requirements are for testing/development environments only
- Ubuntu 20.04 target platform may need updates for current security requirements
- The examples assume root access or sudo privileges for system configuration
- Network connectivity to Chef package repositories is available during deployment
- VM resources meet Chef Automate minimum requirements (specified in deployment scripts)