# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository is a collection of Chef-related examples and deployment scripts rather than a traditional Chef cookbook repository requiring migration. The repository already contains Ansible playbooks and serves as educational content demonstrating Chef InSpec integration with Ansible for compliance automation. No traditional Chef-to-Ansible migration is required, but the repository structure and deployment scripts need modernization and standardization.

## Module Migration Plan

This repository contains example code and deployment utilities that demonstrate Chef InSpec integration with Ansible:

### MODULE INVENTORY

**No traditional Chef cookbooks found** - this repository contains example playbooks and deployment scripts rather than Chef cookbooks requiring migration.

**Existing Ansible Content:**
- **website_https**: 
    - Description: Apache web server with SSL/TLS configuration, self-signed certificate generation, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: SSL certificate generation via OpenSSL, Apache virtual host configuration, package management

- **poodle_fix**:
    - Description: SSL protocol hardening playbook that disables SSLv3 and enforces TLS 1.2 to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL configuration modification, protocol restriction, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol verification
- `tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance (STIG control)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML content for web server testing

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml), with Apache 2.4.41 package version targeting Ubuntu-specific repositories
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **apache2=2.4.41-4ubuntu3.10**: Specific Ubuntu package version - update to use latest available or parameterize for different OS families
- **python3-openssl**: Required for Ansible OpenSSL modules - ensure availability across target environments
- **Test Kitchen with Vagrant**: Consider migration to molecule with Docker or Podman for more portable testing

### Security Considerations
- **Self-signed certificates**: Current playbooks generate self-signed certificates for testing - production deployments should integrate with proper CA or Let's Encrypt
- **Hardcoded credentials**: Deployment scripts contain plaintext passwords and usernames that should be externalized to Ansible Vault or environment variables
- **SSL/TLS configuration**: POODLE fix playbook demonstrates security hardening - ensure TLS 1.3 support and modern cipher suites
- **SSH security**: InSpec profile enforces SSH root login restrictions - maintain these security controls in any infrastructure updates

### Technical Challenges
- **Package version specificity**: Playbooks pin specific Ubuntu package versions that may not be available on other distributions or newer Ubuntu releases
- **Handler naming inconsistency**: Some handlers reference 'apache' while others use 'apache2' - standardize service names
- **Chef server deployment automation**: Bash scripts for Chef server deployment could be converted to Ansible playbooks for better idempotency and error handling
- **Test framework integration**: Current Test Kitchen + InSpec setup works well but consider standardizing on Ansible-native testing approaches

### Migration Order
1. **Standardize existing Ansible content** (low risk, immediate value) - fix handler naming, parameterize OS-specific values
2. **Convert deployment scripts to Ansible** (moderate complexity) - replace bash scripts with proper Ansible playbooks
3. **Modernize testing framework** (low priority) - evaluate molecule vs Test Kitchen for consistency with Ansible ecosystem

### Assumptions
- Repository serves as educational/example content rather than production infrastructure code
- Existing Ansible playbooks are functional and represent the desired end state
- Chef server deployment scripts are used for lab/development environments rather than production
- InSpec integration demonstrates compliance-as-code practices that should be maintained
- Target environments will primarily be Ubuntu/Debian-based systems given the current package specifications
- Self-signed certificates are acceptable for testing/development scenarios
- The repository will continue to serve as example content rather than being deployed as production infrastructure