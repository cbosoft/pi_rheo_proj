using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace control_discrete_simple_1
{
    public partial class Form1 : Form
    {

        //Globals
        double sample_time = 1;                                   //increment by 1s every loop
        int n = 0;                                                  //number of samples processed, similar to time passed
        double time
        {
            get
            {
                return n * sample_time;
            }
        }
        double time_length = 0;
        double n_length
        {
            get
            {
                return time_length / sample_time;
            }
        }
        double set_point = 0;

        //control
        double KP = 0;
        double KI = 0;
        double TD = 0;
        double ISE = 0;

        //manipulation
        double TC = 0;
        double SSG = 0;

        //disturbance
        double dist_TC = 1;
        double dist_SSG = 1;
        
        int run_number = 0;
        //

        double[] ca = new double[0];                                //control action of the controller
        double[] y = new double[0];                                 //output of the process
        //double[] u = new double[0];                                 //process input
        double[] e = new double[0];
        double[] d = new double[0];

        public Form1()
        {
            InitializeComponent();
            //step input at t = 10
            //
        }

        public void do_sim()
        {
            do_sim("Response ");
        }
        public void do_sim(string series_name)
        {
            //random gen
            Random r = new Random();
            double temp_dist = 0;
            //size data variables
            ca = new double[1];
            y = new double[1];
            e = new double[1];
            d = new double[1];

            //input validation
            //NOT DONE
            //WARNING!
            //All data is unchecked programmatically

            //set initial values
            set_point = 0;
            ISE = 0;
            n = 1;

            //get user input
            //manipulation
            SSG = Convert.ToDouble(txtSSG.Text);
            TC = Convert.ToDouble(txtTC.Text);

            //set point
            if (radConstant.Checked)
            {
                set_point = Convert.ToDouble(txtSP1.Text);
            }
            else if (radStep.Checked && Convert.ToDouble(txtSP2.Text) == 0)
            {
                radConstant.Checked = true;
                set_point = Convert.ToDouble(txtSP1.Text);
            }
            //disturbance
            dist_SSG = Convert.ToDouble(txtDistSSG.Text);
            dist_TC = Convert.ToDouble(txtDistTC.Text);
            if (radDistConstant.Checked)
            {
                temp_dist = Convert.ToDouble(txtD1.Text);
            }
            else if (radDistStep.Checked && Convert.ToDouble(txtD2.Text) == 0)
            {
                radDistConstant.Checked = true;
                temp_dist = Convert.ToDouble(txtD1.Text);
            }

            //sim
            time_length = Convert.ToDouble(txtTime.Text);
            sample_time = Convert.ToDouble(txtSampleTime.Text);

            //control
            KP = Convert.ToDouble(txtKC.Text);
            KI = Convert.ToDouble(txtITC.Text);
            TD = Convert.ToDouble(txtDTC.Text);

            //set time previous data
            //before sim begun everything was zero (deviation vars - everything is at normal value)
            ca[0] = 0;
            y[0] = 0;
            e[0] = 0;
            d[0] = 0;

            //Add series to chart and response list
            chart1.Series.Add(series_name + " (run: " + run_number + ")");
            lstResponses.Items.Add(series_name + " (run: " + run_number + ")");
            chart1.Series[run_number].ChartType = System.Windows.Forms.DataVisualization.Charting.SeriesChartType.Line;

            //hide gridlines on chart
            chart1.ChartAreas[0].AxisX.MajorGrid.LineWidth = 0;
            chart1.ChartAreas[0].AxisY.MajorGrid.LineWidth = 0;

            do
            {
                //setpoint
                if (radStep.Checked)
                {
                    if (time == Convert.ToDouble(txtSP2.Text))
                    {
                        set_point = Convert.ToDouble(txtSP1.Text);
                    }
                }
                else if (radRamp.Checked)
                {
                    if ((time - sample_time) == Convert.ToDouble(txtSP2.Text))
                    {
                        set_point = (time - Convert.ToDouble(txtSP2.Text)) * Convert.ToDouble(txtSP1.Text);
                    }
                }
                else if (radNoise.Checked)
                {
                    if (time % 2 == 0)
                    {
                        set_point = Convert.ToDouble(txtSP2.Text) + (Convert.ToDouble(txtSP1.Text) - Convert.ToDouble(txtSP2.Text)) * r.NextDouble();
                    }
                }
                else
                {

                }

                //disturbance
                if (radDistStep.Checked)
                {
                    if (time == Convert.ToDouble(txtD2.Text))
                    {
                        temp_dist = Convert.ToDouble(txtD1.Text);
                    }
                }
                else if (radDistRamp.Checked)
                {
                    if ((time - sample_time) == Convert.ToDouble(txtD2.Text))
                    {
                        temp_dist = (time) * Convert.ToDouble(txtD1.Text) - Convert.ToDouble(txtD2.Text);
                    }
                }
                else if (radDistNoise.Checked)
                {
                    if (time % 2 == 0)
                    {
                        temp_dist = Convert.ToDouble(txtD2.Text) + (Convert.ToDouble(txtD1.Text) - Convert.ToDouble(txtD2.Text)) * r.NextDouble();
                    }
                }
                else
                {

                }

                //increase size of arrays
                ca = add_to_arr(0, ca);
                y = add_to_arr(0, y);
                e = add_to_arr(0, e);
                
                d = add_to_arr(temp_dist, d);

                //do process
                y[n] = ((TC - sample_time) / TC) * y[n - 1] + ((SSG * sample_time) / TC) * ca[n - 1] + ((dist_SSG * sample_time) / dist_TC) * d[n - 1];

                //do control
                e[n] = set_point - y[n];
                if (KP == 0 && KI == 0)
                {
                    ca[n] = set_point;
                }
                else
                {
                    ca[n] = ca[n - 1] + KP * (e[n] - e[n - 1]) + KI * sample_time * e[n];
                }

                //Calculate ISE - Doesn't work?
                ISE += (sample_time) * (Math.Pow(e[n], 2));

                //write chart
                chart1.Series[run_number].Points.Add(y[n]);
                chart1.Series[run_number].Points[n - 1].XValue = time;
                //chart1.Series[(3 * run_number) + 1].Points.Add(e[n]);
                //chart1.Series[(3 * run_number) + 2].Points.Add(set_point);

                //increment n
                n += 1;

            } while (n < (n_length + 1));

            //display ISE
            txtISE.Text = Convert.ToString(ISE);
            //txtISE.Text = "ISE not working";

            //increment run number
            run_number += 1;

            //only show latest run
            lstResponses.SelectedIndex = lstResponses.Items.Count - 1;

            //do stuff with response data
            //MessageBox.Show("Final Response: " + y[n- 1]);
        }

        public double[] add_to_arr(double to_add, double[] add_to)
        {
            double[] temp = new double[add_to.Length + 1];
            Array.Copy(add_to, temp, add_to.Length);
            temp[add_to.Length] = to_add;
            return temp;
        }

        private double[] count_maxima(int series_indx)
        {
            int gradient = 0;
            int last_gradient = 0;
            int maxima_count = 0;
            double first_max_x = 0;

            double[] ys = new double[chart1.Series[series_indx].Points.Count];
            for (int j = 0; j < chart1.Series[series_indx].Points.Count; j++)
            {
                ys[j] = chart1.Series[series_indx].Points[j].YValues[0];
            }

            double last_y = ys[0];

            for (int i = 1; i < ys.Length; i++)
            {
                if (ys[i] > last_y)
                {
                    gradient = 1;
                }
                else if (ys[i] == last_y)
                {
                    gradient = 0;
                }
                else
                {
                    gradient = -1;
                }

                if ((gradient < 0) && (last_gradient >= 0))
                {
                    //gradient used to be climbing, is now falling
                    maxima_count += 1;
                    if (maxima_count == 1)
                    {
                        first_max_x = chart1.Series[series_indx].Points[i].XValue;
                    }
                }
                last_gradient = gradient;
                last_y = ys[i];
            }
            double[] outp = new double[2];
            outp[0] = Convert.ToDouble(maxima_count);
            outp[1] = first_max_x;
            return outp;
        }

        private void btnBegin_Click(object sender, EventArgs e)
        {
            do_sim();
        }

        private void txtTime_TextChanged(object sender, EventArgs e)
        {

        }

        private void btnReset_Click(object sender, EventArgs e)
        {
            chart1.Series.Clear();
            run_number = 0;
            lstResponses.Items.Clear();
            lstResponses.Items.Add("All");
        }

        private void btnPG_Click(object sender, EventArgs e)
        {
            btnReset_Click(null, null);
            double KPfrom = Convert.ToDouble(txtKPfrom.Text);
            double KPto = Convert.ToDouble(txtKPto.Text);
            double KIfrom = Convert.ToDouble(txtKIfrom.Text);
            double KIto = Convert.ToDouble(txtKIto.Text);
            int step = Convert.ToInt32(txtStep.Text);
            for (int i = 0; i < step; i++)
            {
                for (int j = 0; j < step; j++)
                {
                    txtKC.Text = Convert.ToString(KPfrom + ((KPto - KPfrom) / step) * i);
                    txtITC.Text = Convert.ToString(KIfrom + ((KIto - KIfrom) / step) * j);
                    do_sim("KP: " + txtKC.Text + ", KI: " + txtITC.Text);
                    Application.DoEvents();
                }
            }

            int[] maxima_counts = new int[chart1.Series.Count];
            double[] first_maxima = new double[chart1.Series.Count];
            for (int i = 0; i < chart1.Series.Count; i++)
            {
                double[] res = count_maxima(i);
                maxima_counts[i] = Convert.ToInt32(res[0]);
                first_maxima[i] = res[1];
            }

            double smallest_x = 1000;
            int at_index = 0;

            for (int i = 0; i < chart1.Series.Count; i++)
            {
                if ((first_maxima[i] < smallest_x) && (maxima_counts[i] > 0) && (maxima_counts[i] <= 5))
                {
                    at_index = i;
                    smallest_x = first_maxima[i];
                }
            }
            lstResponses.SelectedIndex = at_index + 1;
        }

        private void lstResponses_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (lstResponses.SelectedIndex != 0)
            {
                for (int i = 0; i < chart1.Series.Count; i++)
                {
                    if (i != (lstResponses.SelectedIndex - 1))
                    {
                        chart1.Series[i].Enabled = false;
                    }
                    else
                    {
                        chart1.Series[i].Enabled = true;
                    }
                }
            }
            else
            {
                for (int i = 0; i < chart1.Series.Count; i++)
                {
                    chart1.Series[i].Enabled = true;
                }
            }
        }

        private void radStep_CheckedChanged(object sender, EventArgs e)
        {
            if (radStep.Checked)
            {
                lblSP1.Text = "Final Value:";
                lblSP2.Text = "At Time:";
                txtSP2.Enabled = true;
            }
        }

        private void radRamp_CheckedChanged(object sender, EventArgs e)
        {
            if (radRamp.Checked)
            {
                lblSP1.Text = "Ramp Gradient:";
                lblSP2.Text = "Start Time:";
                txtSP2.Enabled = true;
            }
        }

        private void radNoise_CheckedChanged(object sender, EventArgs e)
        {
            if (radNoise.Checked)
            {
                lblSP1.Text = "Max Value:";
                lblSP2.Text = "Min Value:";
                txtSP2.Enabled = true;
            }
        }

        private void radConstant_CheckedChanged(object sender, EventArgs e)
        {
            if (radConstant.Checked)
            {
                lblSP1.Text = "Value:";
                lblSP2.Text = "--";
                txtSP2.Enabled = false;
            }
        }

        private void radDistOff_CheckedChanged(object sender, EventArgs e)
        {
            if (radDistOff.Checked)
            {
                lblD1.Text = "--";
                lblD2.Text = "--";
                txtD1.Enabled = false;
                txtD2.Enabled = false;
            }
        }

        private void radDistConstant_CheckedChanged(object sender, EventArgs e)
        {
            if (radDistConstant.Checked)
            {
                lblD1.Text = "Value:";
                lblD2.Text = "--";
                txtD1.Enabled = true;
                txtD2.Enabled = false;
            }
        }

        private void ranDistNoise_CheckedChanged(object sender, EventArgs e)
        {
            if (radDistNoise.Checked)
            {
                lblD1.Text = "Max Value:";
                lblD2.Text = "Min Value:";
                txtD1.Enabled = true;
                txtD2.Enabled = true;
            }
        }

        private void radDistRamp_CheckedChanged(object sender, EventArgs e)
        {
            if (radDistRamp.Checked)
            {
                lblD1.Text = "Ramp Gradient:";
                lblD2.Text = "Start Time:";
                txtD1.Enabled = true;
                txtD2.Enabled = true;
            }
        }

        private void radDistStep_CheckedChanged(object sender, EventArgs e)
        {
            if (radDistStep.Checked)
            {
                lblD1.Text = "Final Value:";
                lblD2.Text = "At Time:";
                txtD1.Enabled = true;
                txtD2.Enabled = true;
            }
        }
    }
}
