# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and deployment automation rather than production Chef cookbooks requiring migration. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration, deployment scripts for Chef infrastructure, and testing examples. The migration scope is minimal as most content is already Ansible-based or represents infrastructure deployment rather than configuration management.

## Module Migration Plan

This repository contains demonstration and deployment content rather than traditional Chef cookbooks:

### MODULE INVENTORY

**website-https-demo**:
- Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS security hardening, and Chef InSpec compliance testing
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL protocol enforcement

**poodle-vulnerability-fix**:
- Description: Ansible playbook for SSL/TLS security hardening to address POODLE vulnerability by disabling SSLv3 and enforcing TLSv1.2
- Path: chef-and-ansible/poodle_fix.yml  
- Technology: Ansible (already migrated)
- Key Features: Apache SSL configuration updates, protocol restriction, service restart handling

### Infrastructure Files

- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script with user/org provisioning
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL security
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec security control for SSH root login restrictions
- `chef-and-ansible/index.html`: Static HTML test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml test configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (based on Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

**No external dependencies requiring migration** - The Ansible playbooks use standard modules:
- **apt**: Native Ansible package management (no replacement needed)
- **openssl_***: Ansible community.crypto collection modules (already in use)
- **file/copy**: Core Ansible modules (no replacement needed)

### Security Considerations

**SSL/TLS Certificate Management**: 
- Current approach uses self-signed certificates generated via OpenSSL
- Production migration should integrate with proper certificate authority or Let's Encrypt
- Certificate private keys stored in /etc/apache2/certs/ with 0640 permissions

**SSH Security Hardening**:
- InSpec tests verify SSH root login is disabled (PermitRootLogin no)
- Compliance testing framework already established with Chef InSpec
- Migration should maintain or enhance SSH security controls

**Apache Security Configuration**:
- SSL protocol enforcement (TLSv1.2 only, SSLv3 disabled)
- POODLE vulnerability mitigation already implemented
- Virtual host security with proper directory permissions

### Technical Challenges

**Chef InSpec Integration**:
- Current setup uses Chef InSpec for compliance testing alongside Ansible
- Migration decision needed: maintain InSpec or migrate to Ansible compliance modules
- InSpec provides detailed security control mapping (STIG, CCI references)

**Test Kitchen Workflow**:
- Existing Test Kitchen integration for Ansible playbook testing
- Consider migration to Molecule for Ansible-native testing framework
- Maintain compliance verification capabilities during transition

**Infrastructure Deployment Scripts**:
- Bash scripts for Chef server deployment may become obsolete
- Consider containerization or infrastructure-as-code alternatives (Terraform, Ansible)
- User and organization provisioning logic needs preservation

### Migration Order

1. **Infrastructure Deployment** (immediate priority)
   - Evaluate need for Chef Automate/Server infrastructure
   - Consider Ansible AWX/Tower as alternative automation platform
   
2. **Compliance Testing Framework** (moderate complexity)
   - Assess InSpec vs. Ansible compliance modules
   - Maintain security control mappings and audit requirements
   
3. **Testing Workflow** (low complexity)
   - Migrate from Test Kitchen to Molecule if desired
   - Preserve integration testing capabilities

### Assumptions

- **Repository Purpose**: This appears to be a demonstration/example repository rather than production infrastructure code requiring active migration
- **Chef Infrastructure Dependency**: The deployment scripts suggest an existing or planned Chef infrastructure that may influence migration decisions
- **Compliance Requirements**: The detailed InSpec security controls suggest regulatory or compliance requirements that must be maintained post-migration
- **Testing Framework Preference**: Current Test Kitchen usage indicates familiarity with Chef ecosystem testing tools
- **SSL Certificate Strategy**: Self-signed certificates suggest development/testing environment rather than production deployment
- **Ubuntu Target Platform**: Kitchen configuration specifies Ubuntu 20.04, but production targets may differ
- **Apache Web Server Standard**: Current examples focus on Apache; organization may have different web server preferences
- **Security Control Mapping**: InSpec tests reference specific STIG and CCI controls, indicating formal security compliance requirements that must be preserved in any migration