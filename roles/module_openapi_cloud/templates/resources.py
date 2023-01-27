#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


RESOURCES = [
    "AWS::Backup::BackupVault",
    "AWS::Backup::Framework",
    "AWS::Backup::ReportPlan",
    "AWS::EKS::Cluster",
    "AWS::IAM::Role",
    "AWS::Lambda::CodeSigningConfig",
    "AWS::Lambda::EventSourceMapping",
    "AWS::Lambda::Function",
    "AWS::Logs::LogGroup",
    "AWS::Logs::QueryDefinition",
    "AWS::Logs::ResourcePolicy",
    "AWS::RDS::DBProxy",
    "AWS::Redshift::Cluster",
    "AWS::Redshift::EventSubscription",
    "AWS::S3::AccessPoint",
    "AWS::S3::Bucket",
    "AWS::S3::MultiRegionAccessPoint",
    "AWS::S3::MultiRegionAccessPointPolicy",
    "AWS::S3ObjectLambda::AccessPoint",
    "AWS::S3ObjectLambda::AccessPointPolicy",
    # 0.2.0
    "AWS::EKS::FargateProfile",
    "AWS::DynamoDB::GlobalTable",
    "AWS::EKS::Addon",
    "AWS::IAM::ServerCertificate",
    "AWS::KMS::Alias",
    "AWS::KMS::ReplicaKey",
    "AWS::RDS::DBProxyEndpoint",
    "AWS::Redshift::EndpointAccess",
    "AWS::Redshift::EndpointAuthorization",
    "AWS::Redshift::ScheduledAction",
    "AWS::Route53::DNSSEC",
    "AWS::Route53::KeySigningKey",
    "AWS::CloudTrail::Trail",
    "AWS::CloudTrail::EventDataStore",
    "AWS::CloudWatch::CompositeAlarm",
    "AWS::CloudWatch::MetricStream",
]
