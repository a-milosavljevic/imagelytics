using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace WebApp.Models
{
    public class ClassStatisticsModel
    {
        public string ClassName { get; set; }
        public int ImageCount { get; set; }
        public string Percentage { get; set; }
    }
}