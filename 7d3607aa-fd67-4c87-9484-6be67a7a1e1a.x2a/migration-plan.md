# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains demonstration examples of Chef InSpec integration with Ansible rather than traditional Chef cookbooks. The migration scope is limited as the repository primarily contains Ansible playbooks with Chef InSpec verification tests, plus Chef server deployment scripts. The migration involves consolidating compliance testing into native Ansible approaches and converting deployment scripts to Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec compliance tests and deployment scripts that need individual migration planning:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Ansible playbooks for Apache HTTPS website deployment with Chef InSpec compliance verification tests
- Path: chef-and-ansible/
- Technology: Ansible + Chef InSpec
- Key Features: SSL certificate generation, Apache virtual host configuration, HTTPS compliance testing, SSH security validation

**setup-automate**:
- Description: Bash scripts for deploying Chef Automate and Chef Infra Server infrastructure
- Path: setup-automate/
- Technology: Bash scripts
- Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `website_https.yml`: Ansible playbook for Apache HTTPS site deployment with SSL configuration
- `poodle_fix.yml`: Ansible playbook for SSL protocol hardening (disabling SSLv3, enabling TLSv1.2)
- `website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `ssh_profile.rb`: Chef InSpec compliance profile for SSH security configuration (STIG-based controls)
- `deploy-automate.sh`: Bash script for Chef Automate and Infra Server deployment
- `deploy-chef-server.sh`: Bash script for standalone Chef Infra Server deployment

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml), with RHEL compatibility considerations for SSH STIG controls
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for testing)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with ansible-lint, molecule testing, or native Ansible assert modules
- **Test Kitchen**: Replace with Molecule for Ansible testing framework
- **Chef Automate/Server**: Replace with Ansible AWX/Tower or native Ansible automation platform

### Security Considerations
- SSL/TLS certificate management: Current playbooks use self-signed certificates - consider integration with Let's Encrypt or enterprise CA
- SSH hardening compliance: InSpec SSH profile implements STIG controls that need translation to Ansible security roles
- Credential management: Deployment scripts contain hardcoded passwords that need vault integration
- Apache security configuration: SSL protocol restrictions and virtual host security settings require careful migration

### Technical Challenges
- **Compliance Testing Migration**: Chef InSpec tests provide detailed compliance validation that needs equivalent Ansible testing approaches
- **STIG Control Implementation**: SSH security profile implements specific STIG controls (RHEL-08-000227, V-38607) requiring specialized Ansible security roles
- **Infrastructure Deployment**: Chef server deployment scripts need conversion to Ansible playbooks with proper error handling and idempotency
- **Testing Framework**: Test Kitchen + InSpec workflow needs replacement with Molecule + ansible-lint + native testing

### Migration Order
1. **Apache HTTPS Playbooks** (already Ansible - enhance with native testing)
2. **SSH Security Controls** (convert InSpec profiles to Ansible security roles)
3. **Chef Infrastructure Deployment** (convert bash scripts to Ansible playbooks)
4. **Testing Framework** (implement Molecule testing to replace Test Kitchen + InSpec)

### Assumptions
- The repository serves as a demonstration of Chef InSpec + Ansible integration rather than production cookbooks
- Current Ansible playbooks are functional and only need testing methodology migration
- Chef server deployment is for demonstration/lab environments based on hardcoded credentials
- SSL certificate generation is acceptable for testing but production deployment would require proper CA integration
- Ubuntu 20.04 target environment is suitable for migration, though SSH controls reference RHEL STIG requirements
- Test Kitchen configuration suggests this is primarily a development/testing repository rather than production infrastructure code