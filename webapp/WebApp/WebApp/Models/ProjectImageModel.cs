using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace WebApp.Models
{
    public class ProjectImageModel
    {
        public int Id { get; set; }
        public byte State { get; set; }
        public int ProjectId { get; set; }
        public string Name { get; set; }
        public int Size { get; set; }
        public string ClassName1 { get; set; }
        public string ClassProbability1 { get; set; }
        public string ClassName2 { get; set; }
        public string ClassProbability2 { get; set; }
        public string ClassName3 { get; set; }
        public string ClassProbability3 { get; set; }
        public string ClassName4 { get; set; }
        public string ClassProbability4 { get; set; }
        public string ClassName5 { get; set; }
        public string ClassProbability5 { get; set; }
    }
}
