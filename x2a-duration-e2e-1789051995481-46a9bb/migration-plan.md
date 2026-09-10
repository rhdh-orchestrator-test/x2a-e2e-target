# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible rather than production infrastructure-as-code requiring migration. The content is already primarily Ansible-based with InSpec testing, representing a target state rather than a source requiring migration. However, the setup scripts for Chef Automate/Infra Server deployment could benefit from Ansible automation.

## Module Migration Plan

This repository contains demonstration and setup scripts rather than traditional Chef cookbooks:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
The following components were identified from the actual repository structure:

- **website-https-demo**:
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS hardening, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: OpenSSL certificate generation, Apache virtual host configuration, SSL module activation

- **poodle-ssl-fix**:
    - Description: Ansible playbook for SSL protocol hardening to disable SSLv3 and enforce TLS 1.2 (POODLE vulnerability mitigation)
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL configuration replacement, protocol restriction

- **chef-automate-deployment**:
    - Description: Bash script for automated Chef Automate and Chef Infra Server deployment with user and organization setup
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash scripting
    - Key Features: Hostname configuration, system tuning, Chef Automate CLI deployment, user/org creation

- **chef-server-deployment**:
    - Description: Bash script for standalone Chef Infra Server deployment without Automate components
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash scripting
    - Key Features: Similar to automate deployment but infra-server only

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS configuration and SSL protocol validation
- `tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance (STIG-based controls)
- `index.html`: Static HTML test content for web server validation
- `README.md`: Documentation explaining Chef InSpec and Ansible integration approach

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml), with Chef server deployment targeting Linux systems
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for testing)
- **Cloud Platform**: Not specified - scripts support both on-premises and cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef Automate CLI**: Replace bash deployment scripts with Ansible automation using package management and service modules
- **chef-server-ctl**: Automate user and organization creation through Ansible command modules or Chef Server API calls
- **Test Kitchen**: Already configured for Ansible - no migration needed
- **InSpec**: Already integrated with Ansible workflow - maintain current testing approach

### Security Considerations
- **Hardcoded credentials**: The deployment scripts contain hardcoded passwords and user details that should be externalized to Ansible Vault
  - Username, password, email, and organization details are embedded in bash variables
  - SSL certificate generation uses self-signed certificates - consider integration with proper CA or Let's Encrypt
- **SSH security**: InSpec tests validate SSH root login restrictions - maintain these compliance checks
- **SSL/TLS configuration**: Current playbooks demonstrate proper SSL hardening - preserve these security practices

### Technical Challenges
- **Chef Server API integration**: Converting chef-server-ctl commands to Ansible modules or API calls may require custom modules or uri module usage
- **System tuning parameters**: The sysctl configurations in deployment scripts need proper Ansible sysctl module implementation
- **Service dependencies**: Chef Automate deployment has complex service interdependencies that need careful orchestration in Ansible

### Migration Order
1. **InSpec compliance tests** (already complete - no migration needed)
2. **Apache HTTPS playbooks** (already complete - no migration needed)  
3. **Chef server deployment automation** (convert bash scripts to Ansible playbooks)
4. **Integration testing** (validate Chef server deployment with existing InSpec tests)

### Assumptions
- The repository serves as an example/demonstration rather than production infrastructure requiring migration
- Current Ansible playbooks represent best practices and should be preserved as reference implementations
- Chef server deployment scripts are intended for development/lab environments based on hardcoded credentials
- The Test Kitchen and InSpec integration approach should be maintained in the target Ansible-only environment
- SSL certificate management may need enhancement for production use beyond self-signed certificates
- The bash deployment scripts assume root access and may need privilege escalation handling in Ansible conversion