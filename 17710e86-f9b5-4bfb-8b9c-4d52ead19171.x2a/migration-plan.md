# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and tools rather than traditional Chef cookbooks. The primary content consists of Ansible playbooks that demonstrate Chef InSpec integration for compliance testing, plus Chef server deployment automation scripts. The migration scope is limited as most content is already Ansible-based or consists of deployment utilities that may not require migration.

## Module Migration Plan

This repository contains mixed technologies that need individual assessment for migration planning:

### MODULE INVENTORY

**website-https-demo**:
- Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed SSL certificates, virtual host setup, and SSL protocol hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL/TLS security hardening

**poodle-ssl-fix**:
- Description: Ansible playbook for SSL protocol hardening to disable SSLv3 and enforce TLS 1.2 in Apache configurations
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL configuration remediation, POODLE vulnerability mitigation, service restart handling

**chef-automate-deployment**:
- Description: Bash script for automated deployment of Chef Automate and Chef Infra Server with user and organization provisioning
- Path: setup-automate/deploy-automate.sh
- Technology: Bash scripting
- Key Features: Hostname configuration, kernel parameter tuning, Chef Automate CLI deployment, user/org creation

**chef-server-deployment**:
- Description: Bash script for standalone Chef Infra Server deployment without Automate components
- Path: setup-automate/deploy-chef-server.sh
- Technology: Bash scripting
- Key Features: Chef Infra Server installation, user management, organization setup, certificate generation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS configuration validation
- `tests/ssh_profile.rb`: Chef InSpec security control for SSH root login verification
- `index.html`: Static HTML test content for web server validation
- `README.md`: Documentation explaining Chef InSpec and Ansible integration examples

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml), with Chef server scripts targeting Linux distributions
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for testing)
- **Cloud Platform**: Not specified, designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: The repository demonstrates InSpec integration with Ansible for compliance testing. This dependency should be maintained as InSpec provides valuable security and compliance validation capabilities that complement Ansible automation.
- **Test Kitchen**: Currently used for testing Ansible playbooks with InSpec verification. Consider migrating to Molecule for Ansible-native testing workflows.
- **Apache 2.4.41**: Specific version pinning in playbooks may need updating for target environment compatibility.

### Security Considerations

- **SSL/TLS Configuration**: The existing Ansible playbooks already implement security best practices including:
  - Self-signed certificate generation for development/testing
  - SSL protocol hardening (disabling SSLv3, enforcing TLS 1.2)
  - Proper file permissions for certificate files (0640)
- **SSH Hardening**: InSpec tests verify SSH root login is disabled, following security benchmarks
- **Credential Management**: Chef server deployment scripts contain hardcoded credentials that should be externalized to Ansible Vault or environment variables
- **Certificate Security**: Self-signed certificates are appropriate for testing but production deployments should integrate with proper CA or Let's Encrypt

### Technical Challenges

- **Chef Server Migration**: The bash deployment scripts for Chef Automate and Chef Infra Server would need to be converted to Ansible playbooks for consistency, requiring:
  - Package installation and configuration management
  - Service management and health checks
  - User and organization provisioning via chef-server-ctl commands
- **InSpec Integration**: Maintaining Chef InSpec compliance testing capabilities while using Ansible requires:
  - Proper InSpec profile management
  - Integration with Ansible testing workflows
  - Compliance reporting and remediation workflows
- **Testing Framework**: Migration from Test Kitchen to Molecule for Ansible-native testing

### Migration Order

1. **Chef Server Deployment Scripts** (moderate complexity) - Convert bash scripts to Ansible playbooks for infrastructure consistency
2. **Testing Framework Migration** (low complexity) - Replace Test Kitchen with Molecule for Ansible testing
3. **InSpec Integration Enhancement** (low risk) - Optimize InSpec profile management and reporting within Ansible workflows

### Assumptions

- The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are already properly structured and do not require migration, only potential optimization
- Chef InSpec will continue to be used for compliance testing alongside Ansible automation
- The target environment supports the specific Apache version (2.4.41) or version constraints can be relaxed
- Chef server deployment is still required in the target environment, justifying conversion of bash scripts to Ansible
- Test Kitchen usage indicates a need for automated testing, making Molecule migration valuable
- The hardcoded credentials in deployment scripts are acceptable for development/testing environments or will be externalized during migration
- Ubuntu 20.04 target OS is still appropriate or can be updated to a more recent LTS version
- The self-signed certificate approach is acceptable for the intended use case (development/testing)