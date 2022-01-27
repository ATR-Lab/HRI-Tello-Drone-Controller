using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace RosSharp.RosBridgeClient
{
    public class DroneStream : UnitySubscriber<MessageTypes.Sensor.CompressedImage>
    {
        public RawImage panelImg;

        private Texture2D texture2D;
        public byte[] imageData;
        private bool isMessageReceived;

        protected override void Start()
        {
            base.Start();
            texture2D = new Texture2D(1, 1);
        }

        private void Update()
        {
            if (isMessageReceived)
                ProcessMessage();
        }

        protected override void ReceiveMessage(MessageTypes.Sensor.CompressedImage message)
        {
            imageData = message.data;
            Debug.Log("here's something: " + imageData[40]);
            isMessageReceived = true;
        }

        private void ProcessMessage()
        {
            texture2D.LoadImage(imageData);
            panelImg.GetComponent<RawImage>().texture = texture2D;
            isMessageReceived = false;
        }
    }
}