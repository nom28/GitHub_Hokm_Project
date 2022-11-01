using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Net;
using System.Net.Sockets;
using System.Threading;

namespace HokmAI
{
    public partial class Hokm : Form
    {
        public Hokm()
        {
            InitializeComponent();
            
        }
        private int proportion;
        private int lastWidth;
        private int lastHeight;

        private int turn;
        private string[] myCardsArray;
        private PictureBox[] myCardsPictureArray;

        private void Hokm_Load(object sender, EventArgs e)
        {
            this.lastWidth = this.Width;
            this.lastHeight = this.Height;
            this.proportion = this.Width / this.Height;

            backCards_imageList.ColorDepth = ColorDepth.Depth32Bit;
            backCards_imageList.ImageSize = new Size(255, 255);
            for (int i = 13; i < 0; i++)
            {
                backCards_imageList.Images.Add(Image.FromFile(currentDirectory+@"image\cards_back\card" + i + "_1.png"));
            }
            Image img = cardsOfPlayer2.Image;
            img.RotateFlip(RotateFlipType.Rotate270FlipNone);
            cardsOfPlayer2.Image = img;
            Image img1 = cardsOfPlayer4.Image;
            img1.RotateFlip(RotateFlipType.Rotate90FlipNone);
            cardsOfPlayer4.Image = img1;

        }
        private void Hokm_Resize(object sender, EventArgs e)
        {
            TopPlayerPicture.Location = new Point(((this.Width - TopPlayerPicture.Width) / 2), 10);
            ButtomPlayerPicture.Location = new Point(((this.Width - TopPlayerPicture.Width) / 2), this.Height - ButtomPlayerPicture.Height * 2);
            LeftPlayerPicture.Location = new Point(10, (this.Height / 2) - ButtomPlayerPicture.Height-10);
            RightPlayerPicture.Location = new Point(this.Width - RightPlayerPicture.Width * 2 + 30, (this.Height / 2) - ButtomPlayerPicture.Height-10);
                
            cardsOfPlayer3.Location = new Point(((this.Width - cardsOfPlayer3.Width) / 2), TopPlayerPicture.Height+10);
            cardsOfPlayer2.Location = new Point(LeftPlayerPicture.Width+10, (this.Height-cardsOfPlayer2.Height)/2-30);
            cardsOfPlayer4.Location = new Point(this.Width - RightPlayerPicture.Width-110, (this.Height - cardsOfPlayer4.Height) / 2-30);
            cardsOfPlayer2.Size = new Size(82, 128);
            cardsOfPlayer4.Size = new Size(82, 128);

            strong_label.Location = new Point(Width - strong_label.Width-15, 0);
            sign_picture.Location = new Point(Width - sign_picture.Width-25, strong_label.Height+8);

            int my_cards_height = Height - ButtomPlayerPicture.Height * 4 +5;
            int my_cards_width = Width / 2-360;
            int offset = myCard9.Width+2;
            myCard1.Location = new Point(my_cards_width + offset*0, my_cards_height);
            myCard2.Location = new Point(my_cards_width + offset * 1, my_cards_height);
            myCard3.Location = new Point(my_cards_width + offset * 2, my_cards_height);
            myCard4.Location = new Point(my_cards_width + offset * 3, my_cards_height);
            myCard5.Location = new Point(my_cards_width + offset * 4, my_cards_height);
            myCard6.Location = new Point(my_cards_width + offset * 5, my_cards_height);
            myCard7.Location = new Point(my_cards_width + offset * 6, my_cards_height);
            myCard8.Location = new Point(my_cards_width + offset * 7, my_cards_height);
            myCard9.Location = new Point(my_cards_width + offset * 8, my_cards_height);
            myCard10.Location = new Point(my_cards_width + offset * 9, my_cards_height);
            myCard11.Location = new Point(my_cards_width + offset * 10, my_cards_height);
            myCard12.Location = new Point(my_cards_width + offset * 11, my_cards_height);
            myCard13.Location = new Point(my_cards_width + offset * 12, my_cards_height);

            TopPlayer_play.Location = new Point((Width-TopPlayer_play.Width)/2, (Height-TopPlayer_play.Height)/2-90);
            ButtomPlayer_play.Location = new Point((Width-TopPlayer_play.Width)/2, (Height-TopPlayer_play.Height)/2-10);
            LeftPlayer_play.Location = new Point((Width-TopPlayer_play.Width)/2-TopPlayer_play.Width-3, (Height-TopPlayer_play.Height)/2-50);
            RightPlayer_play.Location = new Point((Width-TopPlayer_play.Width)/2+TopPlayer_play.Width+3, (Height-TopPlayer_play.Height)/2-50);
        }


        public void ExecuteServer()
        {
            IPHostEntry ipHost = Dns.GetHostEntry(Dns.GetHostName());
            IPAddress ipAddr = ipHost.AddressList[0];
            IPEndPoint localEndPoint = new IPEndPoint(ipAddr, 11112);

            Socket listener = new Socket(ipAddr.AddressFamily,
                 SocketType.Stream, ProtocolType.Tcp);

            listener.Bind(localEndPoint);
            listener.Listen(10);

            Console.WriteLine("Waiting connection ... ");
            Socket clientSocket = listener.Accept();

            while (true)
            {
                byte[] bytes = new Byte[1024];
                string data = null;

                while (true)
                {

                    int numByte = clientSocket.Receive(bytes);

                    data += Encoding.ASCII.GetString(bytes,
                                               0, numByte);

                    if (data.IndexOf("<EOF>") > -1)
                        break;
                }
                string[] stringOfData = data.Split('!');
                for(int j = 0; j < stringOfData.Length; j++)
                {
                    data = stringOfData[j];
                    if (data != "")
                    {
                        string data_code = data.Substring(0, 2);
                        if (data_code == "01") //get strong card
                        {
                            string[] data_split = data.Split('-');
                            SetStrong(data_split[1]);
                        }
                        else
                        {
                            if (data_code == "02") //get all my 13 cards
                            {
                                string[] myCards = data.Split('-');
                                setPictureBoxArr();
                                this.myCardsArray = new string[13];
                                for (int i = 1; i < myCards.Length; i++)
                                {
                                    SetMyCard(myCards[i], i - 1);
                                    this.myCardsArray[i] = myCards[i];
                                }
                            }
                            else
                            {
                                if (data_code == "03") // get player and what card he played
                                {
                                    int person = Int32.Parse(data.Split('-')[1]);
                                    string cardPlayed = data.Split('-')[2];
                                    MakeTurn(person, cardPlayed);
                                }
                                else
                                {
                                    if(data_code == "04")
                                    {
                                        string num = data.Split('-')[1];
                                        EndOfTurn(num);
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        public void EndOfTurn(string num)
        {
            TopPlayer_play.Image = null;
            ButtomPlayer_play.Image = null;
            LeftPlayer_play.Image = null;
            RightPlayer_play.Image = null;
            if (num == "0")
            {
                score1.Text = score1.Text + "*";
            }
            else
            {
                score2.Text = score2.Text + "*";
            }
        }
        private string currentDirectory;
        public void SetStrong(string data)
        {            
            sign_picture.Image = Image.FromFile(currentDirectory + @"image\"+ data + ".png");
        }

        private PictureBox[] pb;
        public void setPictureBoxArr()
        {
            pb = new PictureBox[13];
            pb[0] = myCard1;
            pb[1] = myCard2;
            pb[2] = myCard3;
            pb[3] = myCard4;
            pb[4] = myCard5;
            pb[5] = myCard6;
            pb[6] = myCard7;
            pb[7] = myCard8;
            pb[8] = myCard9;
            pb[9] = myCard10;
            pb[10] = myCard11;
            pb[11] = myCard12;
            pb[12] = myCard13;
        }

        public string GetCardFileName(string card)
        {
            char letter = card[0];
            string number = card[1] + "";
            if (card.Length == 3)
            {
                number = card.Substring(1, 2);
            }

            string pic_file_name = number + "_";
            if (letter == 'H')
            {
                pic_file_name += "hearts";
            }
            else
            {
                if (letter == 'C')
                {
                    pic_file_name += "clubs";
                }
                else
                {
                    if (letter == 'S')
                    {
                        pic_file_name += "spades";
                    }
                    else
                    {
                        pic_file_name += "diamonds";
                    }
                }
            }
            return pic_file_name;
        }

        public void SetMyCard(string card, int index)
        {
            string pic_file_name = GetCardFileName(card);
            pb[index].Image = Image.FromFile(currentDirectory+@"image\cards\" + pic_file_name + ".png");
        }
        
        public void MakeTurn(int playerNumber, string cardPlayed)
        {
            string card_file_name = GetCardFileName(cardPlayed);
            string path = currentDirectory+@"image\cards\" + card_file_name + ".png";
            if (playerNumber == 2)
            {
                cardsOfPlayer2.Image = backCards_imageList.Images[turn];
                RightPlayer_play.Image = Image.FromFile(path);
            }
            else
            {
                if (playerNumber == 3)
                {
                    cardsOfPlayer3.Image = backCards_imageList.Images[turn];
                   TopPlayer_play.Image = Image.FromFile(path);
                }
                else
                {
                    if (playerNumber == 4)
                    {
                        cardsOfPlayer4.Image = backCards_imageList.Images[turn];
                        RightPlayer_play.Image = Image.FromFile(path);
                    }
                    else
                    {
                        if (playerNumber == 1)
                        {
                            ButtomPlayer_play.Image = Image.FromFile(path);
                            int number = 1;
                            for(int i = 0; i < this.myCardsArray.Length; i++)
                            {
                                if (myCardsArray[i] == cardPlayed)
                                {
                                    number = i + 1;
                                }
                            }
                            myCardsPictureArray[number].Image = null;
                        }
                    }
                }
            }
        }

        private void Hokm_Shown(object sender, EventArgs e)
        {
            currentDirectory = Environment.CurrentDirectory;
            string[] currentDirectoryArr = currentDirectory.Split('\\');
            string path = "";
            for(int i = 0; i < currentDirectoryArr.Length-2; i++)
            {
                path += currentDirectoryArr[i] + "\\";
            }
            currentDirectory = path;
            this.Width = 830;
            this.Height = 600;
            Thread s = new Thread(new ThreadStart(ExecuteServer));
            s.Start();
            SetStrong("hearts");
            string data = "D4-C4-S7-H14-H8-C2-C12-C11-D6-S2-S6-H12-D9"; 
            string[] myCards = data.Split('-');
            setPictureBoxArr();
            for (int i = 0; i < myCards.Length; i++)
            {
                SetMyCard(myCards[i], i);
            }
            sign_picture.Width = 50;
            sign_picture.Height = 50;
            TopPlayer_play.Image = null;
            ButtomPlayer_play.Image = null;
            RightPlayer_play.Image = null;
            LeftPlayer_play.Image = null;
            turn = 1;
            myCardsPictureArray = new PictureBox[13];
            myCardsPictureArray[0] = myCard1;
            myCardsPictureArray[1] = myCard2;
            myCardsPictureArray[2] = myCard3;
            myCardsPictureArray[3] = myCard4;
            myCardsPictureArray[4] = myCard5;
            myCardsPictureArray[5] = myCard6;
            myCardsPictureArray[6] = myCard7;
            myCardsPictureArray[7] = myCard8;
            myCardsPictureArray[8] = myCard9;
            myCardsPictureArray[9] = myCard10;
            myCardsPictureArray[10] = myCard11;
            myCardsPictureArray[11] = myCard12;
            myCardsPictureArray[12] = myCard13;
            this.Width++;
            this.Width++;
        }

        private void Hokm_ResizeEnd(object sender, EventArgs e)
        {
            //    if (this.Width != this.lastWidth)
            //    {
            //        int change = (this.Width - this.lastWidth) / this.proportion;
            //        this.Height += change;
            //    }
            //    else
            //    {
            //        int change = (this.Height - this.lastHeight) * this.proportion;
            //        this.Width += change;
            //    }
            //    this.lastWidth = this.Width;
            //    this.lastHeight = this.Height;
            //MessageBox.Show($"proportion {proportion} \n width {this.Width} \n height {this.Height}");
        }

        private void label1_Click(object sender, EventArgs e)
        {

        }
    }
}

