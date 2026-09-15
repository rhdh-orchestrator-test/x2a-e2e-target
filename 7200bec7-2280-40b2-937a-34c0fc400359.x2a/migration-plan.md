# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and tooling rather than traditional Chef cookbooks requiring migration. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration for compliance automation, plus Chef server deployment scripts. The migration scope is minimal as most content is already Ansible-based or consists of deployment tooling that can be modernized rather than migrated.

## Module Migration Plan

This repository contains mixed technologies that need individual migration planning:

### MODULE INVENTORY

**website-https-demo**:
- Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed SSL certificates, virtual host setup, and Chef InSpec compliance testing
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, InSpec compliance verification

**poodle-ssl-fix**:
- Description: Ansible playbook for SSL hardening by disabling SSLv3 and enforcing TLS 1.2 to mitigate POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, service restart handlers

**chef-automate-deployment**:
- Description: Bash script for automated deployment of Chef Automate and Chef Infra Server with user and organization provisioning
- Path: setup-automate/deploy-automate.sh
- Technology: Bash scripting
- Key Features: Hostname configuration, kernel parameter tuning, Chef Automate CLI deployment, user/org creation

**chef-server-deployment**:
- Description: Bash script for standalone Chef Infra Server deployment without Automate components
- Path: setup-automate/deploy-chef-server.sh
- Technology: Bash scripting
- Key Features: Similar to automate deployment but infra-server only, user/org provisioning

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with Vagrant driver and InSpec verifier
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality, SSL protocol verification, and port accessibility
- `tests/ssh_profile.rb`: Chef InSpec security control for SSH root login compliance (STIG-based)
- `index.html`: Static HTML test content for web server verification
- `README.md` files: Documentation explaining Chef InSpec and Ansible integration patterns

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Already integrated with Ansible via Test Kitchen verifier - no migration needed, continue using for compliance automation
- **Test Kitchen**: Currently configured for Ansible playbook testing - maintain existing workflow
- **Apache 2.4.41**: Specific version pinned in playbook - verify availability in target repositories
- **OpenSSL Python modules**: python3-openssl package dependency for certificate generation

### Security Considerations

- **SSL/TLS Configuration**: Existing playbooks demonstrate proper SSL hardening practices (TLS 1.2 enforcement, SSLv3 disabling)
- **Certificate Management**: Self-signed certificate generation via Ansible OpenSSL modules - consider migration to proper CA or Let's Encrypt for production
- **SSH Hardening**: InSpec controls verify SSH root login disabled - maintain these compliance checks
- **Credential Management**: Chef server deployment scripts contain hardcoded credentials (username, password, email) - migrate to Ansible Vault or external secret management

### Technical Challenges

- **Chef Server Dependencies**: Deployment scripts rely on Chef Automate CLI and specific Chef server components - modernize to use containerized Chef or migrate to native Ansible Tower/AWX
- **InSpec Integration**: Maintain Chef InSpec for compliance testing while using Ansible for configuration management - this hybrid approach is already demonstrated and working
- **Test Kitchen Workflow**: Existing testing framework is well-established - preserve for continued compliance validation

### Migration Order

1. **Chef Server Deployment Scripts** (moderate complexity) - Convert Bash scripts to Ansible playbooks with proper secret management
2. **Documentation Updates** (low complexity) - Update README files to reflect pure Ansible approach while maintaining InSpec integration guidance
3. **Test Kitchen Configuration** (low complexity) - Verify existing Test Kitchen + Ansible + InSpec workflow continues to function

### Assumptions

- The repository serves as an example/demo collection rather than production infrastructure code
- Chef InSpec will continue to be used for compliance automation alongside Ansible
- The hybrid Chef InSpec + Ansible approach demonstrated here is the intended target architecture
- Chef server deployment is still required for organizations using Chef InSpec at scale
- Test Kitchen workflow for compliance testing will be maintained
- Ubuntu 20.04 target platform will be upgraded to more recent LTS version (22.04 or 24.04)
- Self-signed certificates are acceptable for demo purposes but production deployments will use proper certificate authorities
- The hardcoded credentials in deployment scripts are for demonstration only and will be replaced with proper secret management in production use