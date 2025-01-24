/*
****************************************************************************
*  Copyright (c) 2023,  Skyline Communications NV  All Rights Reserved.    *
****************************************************************************

By using this script, you expressly agree with the usage terms and
conditions set out below.
This script and all related materials are protected by copyrights and
other intellectual property rights that exclusively belong
to Skyline Communications.

A user license granted for this script is strictly for personal use only.
This script may not be used in any way by anyone without the prior
written consent of Skyline Communications. Any sublicensing of this
script is forbidden.

Any modifications to this script by the user are only allowed for
personal use and within the intended purpose of the script,
and will remain the sole responsibility of the user.
Skyline Communications will not be responsible for any damages or
malfunctions whatsoever of the script resulting from a modification
or adaptation by the user.

The content of this script is confidential information.
The user hereby agrees to keep this confidential information strictly
secret and confidential and not to disclose or reveal it, in whole
or in part, directly or indirectly to any person, entity, organization
or administration without the prior written consent of
Skyline Communications.

Any inquiries can be addressed to:

	Skyline Communications NV
	Ambachtenstraat 33
	B-8870 Izegem
	Belgium
	Tel.	: +32 51 31 35 69
	Fax.	: +32 51 31 01 29
	E-mail	: info@skyline.be
	Web		: www.skyline.be
	Contact	: Ben Vandenberghe

****************************************************************************
Revision History:

DATE		VERSION		AUTHOR			COMMENTS

dd/mm/2023	1.0.0.1		Skyline			Initial version.
16/02/2024	1.0.1.1     João Cunha, SP	Optimize script execution logic.
										Implement multicast clamping.
										Introduce additional run-time safeguards.
08/08/2024	1.1.0.0     João Cunha, SP  Resources creation updated to target "Supplier Dynamic" table.
28/08/2024	1.1.1.0		Skyline			Clean script and update it to create non function resources.
06/09/2024 	1.1.2.0		João Cunha, SP	Update for CHG0044988 - Add Paused Interface parameter in DM scripts.							
****************************************************************************
*/
namespace CreateResource_VET
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using Newtonsoft.Json;
    using Skyline.DataMiner.Automation;
    using Skyline.DataMiner.Core.DataMinerSystem.Automation;
    using Skyline.DataMiner.Core.DataMinerSystem.Common;
    using Skyline.DataMiner.Net.Messages;
    using Skyline.DataMiner.Net.ResourceManager.Objects;
    using Capabilities = Skyline.DataMiner.Net.SRM.Capabilities;

    using SLNetMessages = Skyline.DataMiner.Net.Messages;

    /// <summary>
    /// Represents a DataMiner Automation script.
    /// </summary>
    public class Script
    {
        /*---------------------------------------------+
        |             _resourceName                    |
        | +------------------+    +------------------+ |
        | | Stream Input     |    | Stream Output    | |
        | |+----------------+|    |+----------------+| |
        | | - _srtMode       |    | - _srtOutputPort | |
        | | - _srtPullIP     | -> |                  | |
        | | - _srtInputPort  |    |                  | |
        | | - _srtPassphrase |	  |                  | |
        | +------------------+    +------------------+ |
        +---------------------------------------------*/
        /// <summary> The base name for the resources. </summary>
        /// <remarks> The format should be "Supplier_CH". Example: "WB_CH" for Warner Bros. </remarks>
        private readonly string _resourceName = "AZA_CH";

        /// <summary> The instance type. </summary>
        /// <remarks> Should match the supplier's short name. Example: "WB" for Warner Bros. </remarks>
        /// <value> Check it on Profiles > Parameteres > Type. </value>
        private readonly string type = "";

        /// <summary> The host identifier for resource deployment. </summary>
        /// <remarks> Must uniquely identify the ingest host system. 
		/// Supported options: "INX01", "INX02", "INX03". </remarks>
        /// <value> Check it on Profiles > Parameteres > MWEdge. </value>
        private readonly string _edge = "INX03";

        /// <summary> The starting channel number for stream naming. </summary>
        /// <remarks> Determines the stream naming convention and must not be less than <c>_stop</c>.
		/// Example: "_start = 4" results in "WB_CH04". </remarks>
        /// <value> The starting channel number. </value>
        private readonly int _start = 1;

        /// <summary> The ending channel number for stream naming. </summary>
        /// <remarks> Must not be less than <c>_start</c>. 
        /// Otherwise it will create the resouces up until the last available IP for a standard /24 subnet (255). 
        /// Example: "_stop = 16" results in "WB_CH16".</remarks>
        /// <value> The ending channel number. </value>
        private int _stop = 32;

        /// <summary> The GVN channel number for the first stream. </summary>
        /// <remarks> Corresponds to the stream starting from <c>_start</c>. 
		/// Example: "_gvnChannel = 2004" for "WB_CH04". </remarks>
        /// <value> The GVN channel number. </value>
        private readonly int _gvnChannel = 32301;

        /// <summary> SRT stream mode: "Listener" or "Pull". </summary>
        /// <remarks> Use empty IP if mode is "Listener". </remarks>
        /// <value> The SRT stream mode. </value>
        private readonly string _srtModeMain = "Listener";
        private readonly string _srtModeBackup = "Listener";

        /// <summary> The IP address for the stream source when mode is "Pull". </summary>
        /// <remarks> Leave empty if mode is "Listener". </remarks>
        /// <value> The IP address for the stream source. </value>
        private string _srtPullIPMain = "";
        private string _srtPullIPBackup = "";

        /// <summary> Port number for the stream input source. </summary>
        /// <remarks> Port used to receive the stream. </remarks>
        /// <value> The port number for the stream input source. </value>
        private readonly int _srtInputPortMain = 3415;
        private readonly int _srtInputPortBackup = 3515;
        
	    /// <summary> Indicates whether the source is active. </summary>
	    /// <remarks> When false, "|Paused" will be appended to the source (main or backup) input value. 
		/// You most likely wont need to change this. </remarks>
	    private readonly bool _isMainSourceActive = true;
	    private readonly bool _isBackupSourceActive = false;

        /// <summary> The encryption key length for the SRT input stream. </summary>
        /// <remarks> Supported options: "None", "AES-128", "AES-192", "AES-256". Use "None" to disable. </remarks>
        /// <value> The encryption key length. </value>
        private readonly string _srtEncryption = "AES-256";

        /// <summary> The passphrase for the SRT input stream. </summary>
        /// <remarks> Use an empty string "" for no passphrase. </remarks>
        /// <value> The passphrase for the SRT input stream. </value>
        private readonly string _srtPassphraseMain = "";
        private readonly string _srtPassphraseBackup = "";

        /// <summary> The port number for the SRT output stream. </summary>
        /// <remarks> Set to 0 to use the default scheme (<c>_srtInputPort + 1000</c>). </remarks>
        /// <value> The port number for the SRT output stream. </value>
        private readonly int _srtOutputPort = 0;

        /// <summary> Subnet for the UDP multicast for each regional offices. </summary>
        /// <remarks> Example: "20" for Aveiro office will translate to "231.216.20.x" 
		/// AVE: 231.216.xx | LMK: 226.1.xx | YER: 228.33.xx . </remarks>
        /// <value> The UDP multicast range. </value>
        private readonly string _ave_udp_subnet = "20";
        private readonly string _lmk_udp_subnet = "20";
        private readonly string _yer_udp_subnet = "20";

        /// <summary> The last octet of the multicast address. </summary>
        /// <remarks> Ensure <c>_mcastLastOctet + (_stop - _start)</c> does not exceed 255. 
		/// Example: "_mcastLastOctet = 1" for first stream IP. 
		/// You most likely wont have to change this. </remarks>
        /// <value> The last octet of the multicast address. </value>
        private readonly int _mcastLastOctet = 1;

        /// <summary> Flag to create new resources (<c>true</c>) or delete them (<c>false</c>). </summary>
        /// <remarks> Set to <c>false</c> only when deleting resources. 
		/// Example: "_createNewResources = true" to create streams. </remarks>
        /// <value> A flag indicating whether to create or delete resources. </value>
        private readonly bool _createNewResources = true;


        /// <summary> The script entry point for executing the resource creation. </summary>
        /// <param name="engine">Link with SLAutomation process.</param>
        public void Run(IEngine engine)
        {
        	// Multicast Clamping.
            while ((_mcastLastOctet + (_stop - _start + 1)) > 255)
            {
                _stop--;
            }
            int iterationCount = _stop - _start + 1;

            var supplierResourcePool = (engine.SendSLNetSingleResponseMessage(new SLNetMessages.GetResourcePoolMessage
            {
                ResourceManagerObjects = new List<SLNetMessages.ResourcePool>
                {
                	// Resource Pool. Apps > resources > Supplier Dynamic.
                    new SLNetMessages.ResourcePool
                    {
                        Name = "Supplier Dynamic",
                    },
                },
            }) as SLNetMessages.ResourcePoolResponseMessage).ResourceManagerObjects;
            var profileParameters = (engine.SendSLNetSingleResponseMessage(new SLNetMessages.GetProfileManagerParameterMessage
            {
                ManagerObjects = new List<Skyline.DataMiner.Net.Profiles.Parameter>
                {
                    new Skyline.DataMiner.Net.Profiles.Parameter { Name = "Type" },
                    new Skyline.DataMiner.Net.Profiles.Parameter { Name = "ResourceOutputInterfaces" },
                    new Skyline.DataMiner.Net.Profiles.Parameter { Name = "ResourceInputInterfaces" },
                },
            }) as SLNetMessages.ProfileManagerResponseMessage).UpdatedParameters;
            var typeProfileParameter = profileParameters.FirstOrDefault(a => a.Name.Equals("Type"))
                ?? throw new ParameterNotFoundException("Type");
            var resourceOutputInterfacesProfileParameter = profileParameters.FirstOrDefault(a => a.Name.Equals("ResourceOutputInterfaces"))
                ?? throw new ParameterNotFoundException("ResourceOutputInterfaces");
            var resourceInputInterfacesProfileParameter = profileParameters.FirstOrDefault(a => a.Name.Equals("ResourceInputInterfaces"))
                ?? throw new ParameterNotFoundException("ResourceInputInterfaces");
            var resourceOutputInterfaceCapability = new Capabilities.ResourceCapability(resourceOutputInterfacesProfileParameter.ID)
            {
                Value = new Skyline.DataMiner.Net.Profiles.CapabilityParameterValue
                {
                    Discreets = new List<string> { "IP" },
                },
            };
            var resourceInputInterfaceCapability = new Capabilities.ResourceCapability(resourceInputInterfacesProfileParameter.ID)
            {
                Value = new Skyline.DataMiner.Net.Profiles.CapabilityParameterValue
                {
                    Discreets = new List<string> { "IP" },
                },
            };
            var typeCapability = new Capabilities.ResourceCapability(typeProfileParameter.ID)
            {
                Value = new Skyline.DataMiner.Net.Profiles.CapabilityParameterValue
                {
                    Discreets = new List<string> { type },
                },
            };

            var resourceList = new List<Resource>();
            bool _finalCreateNewResources = !_createNewResources;
            // Apps > resources > Supplier Dynamic.
            for (int loopCount = 0; loopCount < iterationCount; loopCount++)
            {
                var resourceName = $"{_resourceName}{(_start + loopCount):00}";
                
                // Check if _srtOutputPort has been defined (non zero), otherwise follow normal (_srtInputPort + 1000) scheme.
                int _finalSrtOutputPort = _srtOutputPort == 0 ? (_srtInputPortMain + 1000 + loopCount) : _srtOutputPort + loopCount;

                // Define final SRT input ports.
                int _finalSrtInputPortMain = _srtInputPortMain + loopCount;
                int _finalSrtInputPortBackup = _srtInputPortBackup + loopCount;
                
                // Construct input values with pause status.
	            string _mainInputValue = $"srt://{_srtPullIPMain}:{_finalSrtInputPortMain}|{_srtModeMain}" + (_isMainSourceActive ? "" : "|Paused");
	            string _backupInputValue = $"srt://{_srtPullIPBackup}:{_finalSrtInputPortBackup}|{_srtModeBackup}" + (_isBackupSourceActive ? "" : "|Paused");
			
                // Calculate the final multicast octet.
                int _finalMcastOctet = _mcastLastOctet + loopCount;

                // Ensure _srtPullIP are empty strings if in Listener mode.
                _srtPullIPMain = _srtModeMain == "Listener" ? "" : _srtPullIPMain;
                _srtPullIPBackup = _srtModeBackup == "Listener" ? "" : _srtPullIPBackup;

                // Ensure passphrase is empty when no encryption is used.
                string _finalSrtPassphraseMain = _srtEncryption == "None" ? "" : _srtPassphraseMain;
                string _finalSrtPassphraseBackup = _srtEncryption == "None" ? "" : _srtPassphraseBackup;

                resourceList.Add(new Resource
                {
                    Name = resourceName,
                    MaxConcurrency = 1,
                    PoolGUIDs = new List<Guid> { supplierResourcePool[0].GUID },
                    Capabilities = new List<Capabilities.ResourceCapability>
                    {
                        typeCapability,
                        resourceOutputInterfaceCapability,
                        resourceInputInterfaceCapability,
                    },
                    Properties = new List<ResourceManagerProperty>
                    {
                        new ResourceManagerProperty
                        {
                            Name = "DC MWEdge",
                            Value = $"{_edge}",
                        },
                        new ResourceManagerProperty
                        {
                            Name = "Encryption",
                            Value = $"{_srtEncryption}",
                        },
                        new ResourceManagerProperty
                        {
                            Name = "Input",
                            Value = _mainInputValue,
                        },
                        new ResourceManagerProperty
                        {
                            Name = "Passphrase Main",
                            Value = $"{_srtPassphraseMain}",
                        },
                        new ResourceManagerProperty
                        {
                            Name = "Input Backup",
                            Value = _backupInputValue,
                        },
                        new ResourceManagerProperty
                        {
                            Name = "Passphrase Backup",
                            Value = $"{_srtPassphraseBackup}",
                        },
                        new ResourceManagerProperty
                        {
                            Name = "Output",
                            Value = $"{_finalSrtOutputPort}",
                        },
                        new ResourceManagerProperty
                        {
                            Name = "Latency",
                            Value = "1000",
                        },
                        new ResourceManagerProperty
                        {
                            Name = "Aveiro Multicast",
                            Value = $"udp://231.216.{_ave_udp_subnet}.{_finalMcastOctet}:1234",
                        },
                        new ResourceManagerProperty
                        {
                            Name = "Limerick Multicast",
    						Value = $"udp://226.1.{_lmk_udp_subnet}.{_finalMcastOctet}:21216",
                        },
                        new ResourceManagerProperty
                        {
                            Name = "Yerevan Multicast",
    						Value = $"udp://228.33.{_yer_udp_subnet}.{_finalMcastOctet}:1234",
                        },
                        new ResourceManagerProperty
                        {
                            Name = "GVN Channel",
                            Value = $"{_gvnChannel + loopCount}",
                        },
                    },
                });
            }

            engine.SendSLNetSingleResponseMessage(new SLNetMessages.SetResourceMessage
            {
                DataMinerID = -1,
                HostingDataMinerID = -1,
                isDelete = _finalCreateNewResources,
                ResourceManagerObjects = resourceList,
            });
        }
    }

    public sealed class StreamData
    {
        public enum ProtocolType
        {
            NA = -1,
            Listener = 1,
            Pull = 0,
        }

        public enum TransmissionType
        {
            NA = -1,
            Multicast = 1,
            Unicast = 0,
        }

        public enum EncryptionType
        {
            None = 0,
            AES128 = 1,
            AES192 = 2,
            AES256 = 3,
        }

        public string DcMwEdge { get; set; }

        public string Name { get; set; }

        public string Protocol { get; set; }

        public ProtocolType Type { get; set; }

        public string IpAddress { get; set; }

        public int Port { get; set; }

        public EncryptionType Encryption { get; set; }

        public int Latency { get; set; }

        public string Passphrase { get; set; }

        public string Fec { get; set; }

        public string LimerickIpAddress { get; set; }

        public string AveiroIpAddress { get; set; }

        public string YerevanIpAddress { get; set; }

        public string Buffer { get; set; }

        public string SourceAddress { get; set; }

        public TransmissionType Transmission { get; set; }

        internal string GetInputString()
        {
            switch (Protocol)
            {
                case "SRT":
                    return Type == ProtocolType.Listener ? $"{Protocol.ToLower()}://:{Port}|Listener" : $"{Protocol.ToLower()}://{IpAddress}:{Port}|Pull";

                case "RTP":
                    return Transmission == TransmissionType.Multicast ? $"{Protocol.ToLower()}://:{Port}|RtpUnicast" : $"{Protocol.ToLower()}://{IpAddress}:{Port}|RtpMulticast";

                case "UDP":
                    return Transmission == TransmissionType.Multicast ? $"{Protocol.ToLower()}://:{Port}|UdpUnicast" : $"{Protocol.ToLower()}://{IpAddress}:{Port}|UdpMulticast";

                default:
                    return String.Empty;
            }
        }
    }
}