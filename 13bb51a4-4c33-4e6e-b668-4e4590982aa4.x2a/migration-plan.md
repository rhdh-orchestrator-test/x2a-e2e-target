# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and infrastructure deployment scripts rather than traditional Chef cookbooks. The migration scope is limited as most content is already in Ansible format or consists of infrastructure setup scripts. The primary migration effort involves consolidating existing Ansible playbooks and replacing Chef infrastructure deployment scripts with Ansible equivalents.

**Timeline Estimate**: 1-2 weeks for a small team
**Complexity**: Low to Medium - mostly infrastructure scripts and existing Ansible content

## Module Migration Plan

This repository contains Chef infrastructure examples and deployment scripts that need individual migration planning:

### MODULE INVENTORY

**website-https-demo**:
- Description: Apache web server with HTTPS/SSL configuration, self-signed certificate generation, and virtual host setup for demonstration purposes
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4 installation, SSL certificate generation via OpenSSL, virtual host configuration, security hardening

**poodle-ssl-fix**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL configuration hardening, POODLE vulnerability mitigation, protocol enforcement

**chef-server-deployment**:
- Description: Chef Infra Server deployment automation for on-premises or cloud VM installation
- Path: setup-automate/deploy-chef-server.sh
- Technology: Bash script
- Key Features: Hostname configuration, system tuning, Chef server installation, user and organization creation

**chef-automate-deployment**:
- Description: Complete Chef Automate and Infra Server deployment with integrated monitoring and compliance
- Path: setup-automate/deploy-automate.sh
- Technology: Bash script
- Key Features: Full Chef Automate stack deployment, system optimization, user provisioning, organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL security
- `tests/ssh_profile.rb`: InSpec security profile for SSH hardening compliance (STIG controls)
- `index.html`: Static HTML test content for web server validation
- `README.md`: Documentation for Chef InSpec and Ansible integration examples

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml), with RHEL compatibility for SSH hardening controls
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for testing)
- **Cloud Platform**: Not specified - designed for on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef Automate CLI**: Replace bash deployment scripts with Ansible roles for infrastructure provisioning
- **Test Kitchen**: Migrate testing framework from Kitchen + InSpec to Ansible Molecule with InSpec integration
- **OpenSSL Python modules**: Already present in Ansible playbooks (python3-openssl package)
- **Apache 2.4**: Specific version pinning needs review for target environment compatibility

### Security Considerations
- **SSL/TLS Configuration**: Existing Ansible playbooks already implement security best practices with TLS 1.2 enforcement
- **SSH Hardening**: InSpec profiles contain STIG-compliant SSH security controls that need Ansible implementation
- **Certificate Management**: Self-signed certificates in demo - production migration requires proper CA integration
- **Credential Management**: Hardcoded credentials in deployment scripts (username, password, email) need Ansible Vault integration
- **Root Access**: Playbooks use root user - should migrate to privilege escalation with sudo

### Technical Challenges
- **Chef Infrastructure Replacement**: Deployment scripts install Chef server/Automate - need equivalent Ansible infrastructure or migration to different tools
- **InSpec Integration**: Existing compliance tests use InSpec - maintain compatibility or migrate to Ansible-native testing
- **Test Framework Migration**: Kitchen.yml configuration needs conversion to Molecule for Ansible-native testing
- **Hardcoded Values**: Multiple hardcoded values in scripts need parameterization and variable management

### Migration Order
1. **website-https-demo** and **poodle-ssl-fix** (already in Ansible - consolidate and enhance)
2. **InSpec test migration** (convert compliance tests to Ansible-compatible format)
3. **Chef infrastructure replacement** (replace deployment scripts with Ansible infrastructure roles)
4. **Testing framework** (migrate from Test Kitchen to Molecule)

### Assumptions
- Target environment will not require Chef Infra Server or Automate (infrastructure migration needed)
- InSpec compliance testing framework will be retained alongside Ansible
- Ubuntu/Debian package management is acceptable for target environment
- Self-signed certificates are acceptable for demo purposes (production needs proper PKI)
- Current hardcoded credentials and configuration values will be parameterized
- Test Kitchen dependency can be replaced with Ansible Molecule for testing workflow
- SSH hardening requirements follow RHEL 8 STIG controls as implemented in existing InSpec profiles