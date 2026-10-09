# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and tools rather than traditional Chef cookbooks requiring migration. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration, Chef server deployment scripts, and compliance testing examples. The migration scope is minimal as most content is already Ansible-based or consists of deployment utilities.

## Module Migration Plan

This repository contains mixed technologies that need individual migration planning:

### MODULE INVENTORY

**website-https-demo**:
- Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed SSL certificates, virtual host setup, and SSL protocol hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL/TLS security hardening

**poodle-fix-demo**:
- Description: Ansible playbook for SSL protocol hardening to address POODLE vulnerability by disabling SSLv3 and enforcing TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL configuration remediation, protocol restriction, service restart handling

**chef-automate-deployment**:
- Description: Bash script for automated deployment of Chef Automate and Chef Infra Server with user and organization provisioning
- Path: setup-automate/deploy-automate.sh
- Technology: Bash scripting
- Key Features: Hostname configuration, system tuning, Chef Automate CLI deployment, user/org creation

**chef-server-deployment**:
- Description: Bash script for standalone Chef Infra Server deployment without Automate components
- Path: setup-automate/deploy-chef-server.sh
- Technology: Bash scripting
- Key Features: Chef server installation, user management, organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security control for SSH root login restrictions (STIG compliance)
- `chef-and-ansible/index.html`: Static HTML test file for web server validation
- `README.md`: Repository documentation explaining Chef InSpec and Ansible integration examples

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml), with RHEL compatibility indicated in InSpec tests
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for testing)
- **Cloud Platform**: Not specified - examples are cloud-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Already integrated with Ansible playbooks for compliance testing - no migration needed
- **Test Kitchen**: Currently configured for Ansible provisioner - maintain existing setup
- **Apache 2.4.41**: Specific version pinned in playbooks - verify availability in target repositories
- **OpenSSL/PyOpenSSL**: Required for certificate generation - ensure python3-openssl package availability

### Security Considerations

- **SSL/TLS Configuration**: Existing playbooks implement security best practices (TLS 1.2 enforcement, SSLv3 disabling)
- **Certificate Management**: Self-signed certificates used for demonstration - consider certificate authority integration for production
- **SSH Hardening**: InSpec tests validate SSH root login restrictions per STIG requirements
- **Credential Patterns**: 
  - Hardcoded credentials in Chef deployment scripts (userpassword='password')
  - No encrypted data bags or vault usage detected
  - SSL certificate files stored in /etc/apache2/certs with restricted permissions (0640)

### Technical Challenges

- **Bash Script Migration**: Chef server deployment scripts need conversion to Ansible playbooks for consistency and idempotency
- **InSpec Integration**: Maintain existing Chef InSpec testing framework alongside Ansible automation
- **Version Dependencies**: Apache package version pinning may require updates for newer Ubuntu releases
- **Test Kitchen Compatibility**: Ensure continued Test Kitchen functionality with migrated components

### Migration Order

1. **No Migration Required** - Ansible playbooks (website_https.yml, poodle_fix.yml) are already in target format
2. **Bash Script Conversion** - Convert Chef server deployment scripts to Ansible playbooks for better maintainability
3. **Documentation Updates** - Update README files to reflect any changes in deployment procedures

### Assumptions

- The repository serves as a demonstration/example collection rather than production infrastructure code
- Chef InSpec will continue to be used for compliance testing alongside Ansible
- Test Kitchen integration with Ansible provisioner will be maintained
- The target audience requires both Chef and Ansible knowledge for compliance automation workflows
- Hardcoded credentials in deployment scripts are acceptable for demonstration purposes but should be parameterized for production use
- Ubuntu 20.04 remains the target platform, though RHEL compatibility is implied by STIG references in InSpec tests
- Self-signed certificates are sufficient for demonstration purposes but production deployments would require proper CA-signed certificates