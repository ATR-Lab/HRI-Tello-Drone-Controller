/* 
 * This message is auto generated by ROS#. Please DO NOT modify.
 * Note:
 * - Comments from the original code will be written in their own line 
 * - Variable sized arrays will be initialized to array of size 0 
 * Please report any issues at 
 * <https://github.com/siemens/ros-sharp> 
 */



using RosSharp.RosBridgeClient.MessageTypes.Std;

namespace RosSharp.RosBridgeClient.MessageTypes.H264ImageTransport
{
    public class H264Packet : Message
    {
        public const string RosMessageName = "h264_image_transport/H264Packet";

        public Header header { get; set; }
        public byte[] data { get; set; }

        public H264Packet()
        {
            this.header = new Header();
            this.data = new byte[0];
        }

        public H264Packet(Header header, byte[] data)
        {
            this.header = header;
            this.data = data;
        }
    }
}
