# MIGRATION FROM CHEF INFRASTRUCTURE TO ANSIBLE

This repository contains Chef-related infrastructure deployment scripts and Ansible playbook examples rather than traditional Chef cookbooks requiring migration. The primary content consists of existing Ansible playbooks with Chef InSpec compliance testing, deployment automation for Chef infrastructure, and demonstration materials. The migration scope is minimal as the automation content is already in Ansible format.

## Module Migration Plan

This repository contains infrastructure deployment scripts and example configurations rather than traditional Chef cookbooks:

### MODULE INVENTORY

**No Chef cookbooks or recipes found for migration.** This repository contains:

- **website-https-demo**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS security hardening, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: OpenSSL certificate generation, Apache virtual host configuration, SSL module activation

- **poodle-ssl-fix**:
    - Description: Ansible playbook for SSL security hardening to address POODLE vulnerability by disabling SSLv3 and enforcing TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml  
    - Technology: Ansible (already migrated)
    - Key Features: SSL protocol configuration, Apache SSL module hardening

### Infrastructure Files

- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script for on-premises or cloud VMs
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script without Automate
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Chef InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL/TLS security validation
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance (STIG control)
- `chef-and-ansible/index.html`: Static HTML test content for web server validation

### Target Details

Based on the Ansible playbook configurations:

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml and playbook package versions)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen for local development and testing)
- **Cloud Platform**: Not specified (deployment scripts support both on-premises and cloud VMs)

## Migration Approach

### Key Dependencies to Address

**No external Chef dependencies requiring migration.** The existing Ansible playbooks use standard modules:
- **apache2 (2.4.41-4ubuntu3.10)**: Already configured via Ansible apt module
- **openssl/python3-openssl**: Certificate management handled by Ansible openssl_* modules
- **curl**: Standard utility for HTTP testing and downloads

### Security Considerations

**Existing security configurations in Ansible format:**
- SSL/TLS hardening: POODLE vulnerability mitigation by disabling SSLv3 and enforcing TLS 1.2 only
- Certificate management: Self-signed certificate generation with proper file permissions (0640 for private keys)
- SSH security: InSpec compliance testing for SSH root login restrictions (STIG control RHEL-08-000227)
- File permissions: Proper ownership and permissions for web content and configuration files
- Service management: Secure restart handlers for Apache and SSH services

**Vault/secrets management:**
- Hardcoded credentials: Test environment credentials visible in deployment scripts (userpassword='password')
- SSL certificates: Self-signed certificates generated dynamically, no external certificate management
- No encrypted data bags or Chef Vault usage detected
- Deployment scripts contain plaintext organizational credentials for Chef server setup

### Technical Challenges

**Minimal migration complexity identified:**
- Infrastructure deployment: Chef Automate/Server deployment scripts are infrastructure provisioning, not configuration management requiring migration
- Testing integration: Test Kitchen + InSpec workflow already validates Ansible playbooks, providing compliance verification framework
- Documentation gap: Repository serves as example/demo content rather than production infrastructure requiring systematic migration

### Migration Order

**No traditional migration required.** Recommended actions:

1. **Security hardening** (immediate): Replace hardcoded credentials in deployment scripts with secure credential management
2. **Documentation update** (low priority): Update README files to clarify the repository's purpose as Ansible examples with Chef InSpec testing
3. **Infrastructure assessment** (if applicable): Evaluate whether Chef Automate/Server infrastructure is still needed if migrating away from Chef ecosystem

### Assumptions

- This repository serves as demonstration/example content rather than production Chef cookbooks requiring migration
- The existing Ansible playbooks represent the target state rather than source content needing conversion
- Chef InSpec testing framework will be retained for compliance validation alongside Ansible automation
- Chef Automate/Server deployment scripts may become obsolete if the organization is fully migrating away from Chef infrastructure
- Test Kitchen integration with Ansible and InSpec represents a hybrid testing approach that may be valuable to maintain
- The Ubuntu 20.04 target environment specified in configurations is still the desired deployment target
- Self-signed certificates in examples are acceptable for demonstration purposes but would need proper CA-signed certificates in production
- SSH and SSL security configurations align with organizational security policies and compliance requirements